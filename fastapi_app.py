import asyncio
import json
import logging
import os
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
import aio_pika
import jwt

# логирование чтобы видеть уведомления в консоли
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FastAPI-NotificationService")

app = FastAPI(title="Notification Service")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
QUEUE_NAME = "ticket_updates"

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") 
ALGORITHM = "HS256"

class ConnectionManager:
    def __init__(self):
        # Храним активные вебсокеты в формате: { "user_email": websocket_object }
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, email: str):
        await websocket.accept()
        self.active_connections[email] = websocket
        logger.info(f"🔌 Пользователь {email} подключился к WebSockets")

    def disconnect(self, email: str):
        if email in self.active_connections:
            del self.active_connections[email]
            logger.info(f"Пользователь {email} отключился от WebSockets")

    async def send_personal_message(self, message: dict, email: str):
        if email in self.active_connections:
            websocket = self.active_connections[email]
            await websocket.send_json(message)
            logger.info(f"Уведомление отправлено в браузер пользователя {email}")

manager = ConnectionManager()

@app.websocket("/ws/notifications/")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("email") # payload.get("user_id") 
        
        if not user_email:
            await websocket.close(code=4003)  # Forbidden
            return
            
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        logger.warning(f"Попытка подключения с невалидным JWT токеном: {e}")
        await websocket.close(code=4003)
        return

    user_email = str(user_email)
    await manager.connect(websocket, user_email)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_email)

async def consume_rabbitmq_messages():
    await asyncio.sleep(5)
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        
        logger.info("FastAPI connected to RabbitMQ")
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    data = json.loads(message.body.decode())
                    
                    status = data.get("status")
                    if status == "PRG":
                        ticket_title = data.get("title")
                        spec_name = data.get("specialist_name", "Специалист")
                        ticket_id = data.get("ticket_id")
                        client_email = str(data.get("client_email"))
                        
                        payload_to_frontend = {
                            "type": "ticket_assigned",
                            "ticket_id": ticket_id,
                            "message": f"Специалист {spec_name} взял в работу ваш тикет '{ticket_title}'"
                        }
                        
                        await manager.send_personal_message(payload_to_frontend, client_email)
                        
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_rabbitmq_messages())

@app.get("/")
def read_root():
    return {"status": "FastAPI Notification Service is running successfully"}
