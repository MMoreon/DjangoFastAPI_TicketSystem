import json
import os
import time
import pika
import requests
from celery import shared_task
from django.conf import settings
from celery.signals import worker_ready
from prometheus_client import Histogram, Counter, start_http_server
from .models import Ticket

OLLAMA_URL = "http://ollama:11434/api/generate"
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
QUEUE_NAME = "ticket_updates"

@worker_ready.connect
def start_metrics_server(**kwargs):
    start_http_server(8001)

OLLAMA_TIME = Histogram(
    "helpdesk_ollama_generation_seconds",
    "Сколько секунд думает Qwen 2.5",
    buckets=[1.0, 3.0, 5.0, 10.0, 15.0, 30.0, 60.0]
)
OLLAMA_ERRORS = Counter("helpdesk_ollama_errors_total", "Ошибки Ollama")

def notify_fastapi_ws(payload: dict):
# Отправляет событие в очередь RabbitMQ для FastAPI
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        # Подставьте имя очереди, которую слушает ваш fastapi_app.py
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f"Ошибка отправки уведомления в RabbitMQ: {e}")

@shared_task(bind=True, max_retries=2, default_retry_delay=10)
def generate_ai_suggestion(self, ticket_id: int):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        return


    if ticket.status != "OPN":
        return

    prompt = (
        "Ты — виртуальный ассистент техподдержки. Обращайся напрямую к пользователю на «вы». "
        "Не пиши вступительных фраз вроде «Конечно!» или «Вот несколько шагов». "
        "Сразу дай 3 коротких и безопасных совета, что проверить прямо сейчас, пока оператор подключается к заявке.\n\n"
        f"Проблема: {ticket.title}\n"
        f"Подробности: {ticket.description}"
    )

    payload = {
        "model": "qwen2.5:3b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2, 
            "num_predict": 300  # длинна ответа
        }
    }
    with OLLAMA_TIME.time():
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            response.raise_for_status()
            ai_text = response.json().get("response", "").strip()

            # Повторно проверяем статус перед сохранением, вдруг спец взял тикет за эти секунды
            ticket.refresh_from_db()
            if ticket.status == "OPN" and ai_text:
                ticket.ai_suggestion = ai_text
                ticket.save(update_fields=["ai_suggestion"])
                
                # Пушим подсказку в персональный WebSocket-канал автора тикета
                notify_fastapi_ws({
                    "event": "ai_suggestion",
                    "client_email": ticket.user.email,  #FastAPI извлекает email получателя из сообщения
                    "ticket_id": ticket.id,
                    "ai_suggestion": ai_text,
                })

        except requests.RequestException as exc:
            OLLAMA_ERRORS.inc()
            # Если контейнер ollama еще прогревается при старте — повторим через 10 секунд
            raise self.retry(exc=exc)
