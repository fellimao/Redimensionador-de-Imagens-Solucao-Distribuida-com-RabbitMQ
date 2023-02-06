from rest_framework import viewsets, status
from django.conf import settings
import pika, json, base64
from rest_framework.permissions import IsAdminUser

from .serializers import ImagemSerializer
from .models import Imagem


class ImagemViewSet(viewsets.ModelViewSet):
    queryset = Imagem.objects.all()

    serializer_class = ImagemSerializer

    lookup_field = 'id'

    # Realiza o cadastro na base de dados e envia uma solicitação no broker para o processamento
    def perform_create(self, serializer):
        imagem = serializer.save()

        # Caso estiver executando os testCases, não envia ao broker
        if not settings.TESTING:
            with open(imagem.arquivo.path, 'rb') as f:
                imagem_base64 = base64.b64encode(f.read()).decode('utf-8')

            message = {'id': imagem.id, 'caminho': imagem.arquivo.path, 'arquivo': imagem_base64}

            # Realiza o envio da requisição para o rabbitMq
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.MESSAGE_BROKER_HOST))
            channel = connection.channel()
            channel.queue_declare(queue=settings.REQUESTS_QUEUE)
            channel.basic_publish(exchange='', routing_key=settings.REQUESTS_QUEUE, body=json.dumps(message))
            connection.close()

    # Só podera fazer o update caso seja usuario admin ou o próprio sistema
    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAdminUser]
        return [permission() for permission in self.permission_classes]

    # Apaga row na base de dados e o arquivo
    def perform_destroy(self, instance):
        instance.arquivo.delete()
        instance.delete()




