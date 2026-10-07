import pika
import json

def send_ticket_update_to_queue(ticket_id, title, status, client_email, specialist_name=None, specialist_email=None):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()

        # durable=True чтобы сообщения не терялись при перезагрузке
        channel.queue_declare(queue='ticket_updates', durable=True)

        message_body = {
            "ticket_id": ticket_id,
            "title": title,
            "status": status,
            "client_email": client_email,
            "specialist_name": specialist_name,
            "specialist_email": specialist_email
        }

        channel.basic_publish(
            exchange='',
            routing_key='ticket_updates',
            body=json.dumps(message_body),
            properties=pika.BasicProperties(
                delivery_mode=2,  # персистентн
            )
        )
        connection.close()
    except Exception as e:
        print(f"Ошибка отправки сообщения в RabbitMQ: {e}")
