import random

import websocket
from locust import HttpUser, between, task


class HelpdeskUser(HttpUser):
    # пауза между действиями юзера 2 5 сек
    wait_time = between(2, 5)
    ws = None

    def on_start(self):
        """Выполняется 1 раз при старте каждого виртуального юзера: регистрация/логин + WS"""
        self.email = f"loadtest_{random.randint(1, 100000)}@test.com"
        self.password = "StrongPass123!"

        self.client.post(
            "/auth/register/",
            json={"email": self.email, "name": "Load Tester", "password": self.password},
        )

        resp = self.client.post(
            "/auth/token/", json={"email": self.email, "password": self.password}
        )
        if resp.status_code == 200:
            self.token = resp.json().get("access")
            self.headers = {"Authorization": f"Bearer {self.token}"}

            try:
                self.ws = websocket.create_connection(
                    f"ws://127.0.0.1/ws/notifications/?token={self.token}", timeout=5
                )
            except Exception:
                pass
        else:
            self.headers = {}

    def on_stop(self):
        """Закрываем сокет при остановке теста"""
        if self.ws:
            self.ws.close()

    @task(5)  # просмотр ленты происходит в 5 раз чаще создания тикетов
    def get_tickets(self):
        self.client.get("/tickets/", headers=self.headers, name="/tickets/ [GET]")

    @task(1)  # создание RabbitMQ > Celery > Ollama
    def create_ticket(self):
        self.client.post(
            "/tickets/",
            json={
                "title": "Не работает VPN на рабочем ноутбуке",
                "description": "При подключении выдает ошибку 809, интернет при этом есть.",
            },
            headers=self.headers,
            name="/tickets/ [POST + AI]",
        )
