import json
import os

import coalition_service.coalition_service_pb2 as coalition_pb2
import coalition_service.coalition_service_pb2_grpc as coalition_pb2_grpc
import grpc
import pika
from dotenv import load_dotenv


load_dotenv()
coalition_service_channel = grpc.insecure_channel(f'{os.getenv("COALITION_SERVICE_HOST")}:{os.getenv("COALITION_SERVICE_PORT")}')
coalition_service_stub = coalition_pb2_grpc.CoalitionServiceStub(coalition_service_channel)


def callback(ch, method, properties, body):
    message_body = body.decode('utf-8')
    data = json.loads(message_body)
    request = coalition_pb2.SetCoalitionMemberRequest(login=data["login"], school_user_id=data["school_user_id"])
    response = coalition_service_stub.set_coalition_member(request)
    if response.status != 0:
        print("UNSUCCESS")
    print(f" [x] SUCCESS for {data['login']}")


# Подключение к серверу RabbitMQ
credentials = pika.PlainCredentials(username='garroshm', password='Mongol2022')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=credentials))
channel = connection.channel()

# Создание очереди (если её нет)
channel.queue_declare(queue='actualizator_queue')

# Установка callback-функции для обработки сообщений
channel.basic_consume(queue='actualizator_queue', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit, press CTRL+C')
# Запуск бесконечного цикла для ожидания новых сообщений
channel.start_consuming()
