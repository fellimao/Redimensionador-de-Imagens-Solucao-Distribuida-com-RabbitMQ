import base64
import io
import json
import pika
import time
import pathlib
from PIL import Image
from acoes import ImageResizer
import settings


# Função focada em enviar o resultado do processamento na fila de resultados
def send_processed_image(message) -> None:
    connection_return = pika.BlockingConnection(pika.ConnectionParameters(host=settings.MESSAGE_BROKER_HOST))
    channel_return = connection_return.channel()
    channel_return.queue_declare(queue=settings.RESULTS_QUEUE)
    channel_return.basic_publish(exchange='', routing_key=settings.RESULTS_QUEUE, body=json.dumps(message))
    connection_return.close()


# Realiza o processamento da mensagem, chama o processamento da imagem e marca como consumida
def process_message(ch, method, properties, body) -> None:
    message = json.loads(body)
    file_extension = pathlib.Path(message['caminho']).suffix
    id = message['id']
    imagem_base64 = message['arquivo']

    # Chama a função para o processamento da imagem
    imagem_redimensionada = ImageResizer.ImageResizer(imagem_base64, file_extension, 384, 384)
    print(' [*] Imagem redimensionada')

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(' [*] Consumida a mensagem')

    message = {'id': id, 'caminho': message['caminho'], 'arquivo': imagem_redimensionada}

    # Envia a imagem processada
    send_processed_image(message)

    print(' [*] Realizado envio dos resultados ao broker')


# Inicia a conexão com a fila de solicitações, se tiver alguma mensagem, começa a consumir
def start_consuming_queue() -> None:
    connection = None
    while not connection:
        print(' [*] ImageProcessor tentando conectar')
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.MESSAGE_BROKER_HOST))
        except:
            time.sleep(5)
    channel = connection.channel()
    channel.queue_declare(queue=settings.REQUESTS_QUEUE)
    channel.basic_consume(queue=settings.REQUESTS_QUEUE, on_message_callback=process_message, auto_ack=False)
    print(' [*] ImageProcessor ativo esperando por solicitações')
    channel.start_consuming()


if __name__ == '__main__':
    start_consuming_queue()
