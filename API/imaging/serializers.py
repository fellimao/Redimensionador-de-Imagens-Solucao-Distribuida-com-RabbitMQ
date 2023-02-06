from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Imagem


def validate_file_extension(value):
    if not value.name.endswith(('.png', '.jpg', '.jpeg')):
        raise ValidationError("O arquivo precisa ter a extensão .png ou .jpg")


class ImagemSerializer(serializers.ModelSerializer):
    status_processamento = serializers.CharField(read_only=True)
    arquivo = serializers.ImageField(validators=[validate_file_extension])

    class Meta:
        model = Imagem
        fields = ['id', 'arquivo', 'data_upload', 'status_processamento']
