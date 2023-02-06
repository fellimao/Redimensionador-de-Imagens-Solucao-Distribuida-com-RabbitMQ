from django.conf import settings
import pika
import io
import json
import time
import base64
from PIL import Image
from imaging.models import Imagem


# Nessa função foca em receber o json da mensagem, atualiza a imagem e muda o status para finalizado
def atualiza_imagem(body) -> None:
    message = json.loads(body)
    imagem = message['arquivo']

    # Conversão da imagem decodificando e salvando no lugar da antiga
    imagem_base64 = base64.b64decode(imagem)
    img = Image.open(io.BytesIO(imagem_base64))
    img.save(message['caminho'])
    if not settings.TESTING:
        print(' [*] Salva imagem')

    # Pega o id da row e atualiza o status
    row = Imagem.objects.get(pk=message['id'])
    row.status_processamento = "Finalizada"
    row.save()
    if not settings.TESTING:
        print(' [*] Atualizado Status da imagem')


# Chama a função para atualizar a imagem e marca a mensagem como consumida
def process_message(ch, method, properties, body) -> None:
    print(' [*] Adquirida mensagem')
    atualiza_imagem(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(' [*] Consumida mensagem')


# Inicia a conexão com a fila de resultados, se tiver alguma mensagem, começa a consumir
def start_consuming_queue() -> None:
    connection = None
    while not connection:
        print(' [*] ConsumerDjangoAPI tentando conectar')
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.MESSAGE_BROKER_HOST))
        except:
            time.sleep(5)

    channel = connection.channel()
    channel.queue_declare(queue=settings.RESULTS_QUEUE)
    channel.basic_consume(queue=settings.RESULTS_QUEUE, on_message_callback=process_message, auto_ack=False)
    print(' [*] ConsumerDjangoAPI ativo esperando por resultados')
    channel.start_consuming()


def run():
    start_consuming_queue()
