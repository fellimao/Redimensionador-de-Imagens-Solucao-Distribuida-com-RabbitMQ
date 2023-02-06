from django.db import models
from django.core.validators import FileExtensionValidator


class Imagem(models.Model):
    id = models.AutoField(primary_key=True)
    arquivo = models.ImageField(upload_to='')
    data_upload = models.DateTimeField(auto_now_add=True)
    status_processamento = models.CharField(max_length=50, default='Pendente')
