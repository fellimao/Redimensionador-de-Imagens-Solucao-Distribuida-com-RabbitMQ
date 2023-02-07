from django.test import TestCase, Client
from rest_framework import status
from django.conf import settings
from .models import Imagem
from .scripts import ConsumerResults
import os
import glob
import shutil
import base64
import json


class ImagemTestCase(TestCase):

    # Prepara o caminho para a imagem de teste e copia para a pasta imagens propriamente dita
    def setUp(self) -> None:
        self.client = Client()

        # Preparando imagem de teste
        caminho_imagem_teste_verdadeiro = os.path.join(settings.MEDIA_ROOT, 'testes/imagem_teste.png')
        shutil.copy(caminho_imagem_teste_verdadeiro, settings.MEDIA_ROOT)
        self.caminho_imagem_teste = os.path.join(settings.MEDIA_ROOT, 'imagem_teste.png')

        # Preparando txt de teste
        caminho_txt_teste_verdadeiro = os.path.join(settings.MEDIA_ROOT, 'testes/teste.txt')
        shutil.copy(caminho_txt_teste_verdadeiro, settings.MEDIA_ROOT)
        self.caminho_txt_teste = os.path.join(settings.MEDIA_ROOT, 'teste.txt')

    # Após rodar os testes, remove as imagens e txts sobressalentes
    def tearDown(self) -> None:
        os.remove(os.path.join(settings.MEDIA_ROOT, 'teste.txt'))
        for arquivo in glob.glob(os.path.join(settings.MEDIA_ROOT, 'imagem_teste*')):
            os.remove(arquivo)

    # Testando cadastro da imagem
    def test_upload_imagem(self) -> None:
        print(' [*] Teste de cadastro')
        with open(self.caminho_imagem_teste, "rb") as imagem_teste:
            response = self.client.post('/imaging/', {'arquivo': imagem_teste, 'teste': True})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Imagem.objects.count(), 1)

    # Testando cadastro com arquivo que não é imagem
    def test_upload_txt(self) -> None:
        print(' [*] Teste de cadastro com algo que não é imagem')
        with open(self.caminho_txt_teste, "rb") as txt_teste:
            response = self.client.post('/imaging/', {'arquivo': txt_teste, 'teste': True})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Imagem.objects.count(), 0)

    # Testando obtenção de imagem pela API
    def test_get_imagem_specific(self) -> None:
        print(' [*] Teste de busca de objeto')
        imagem = Imagem.objects.create(arquivo=self.caminho_imagem_teste)
        response = self.client.get('/imaging/{}/'.format(imagem.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Testando deleção da imagem (banco e arquivo) após ter sido processada
    def test_delete_imagem(self) -> None:
        print(' [*] Teste de deleção')
        imagem = Imagem.objects.create(arquivo=self.caminho_imagem_teste)

        response = self.client.delete('/imaging/{}/'.format(imagem.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Imagem.objects.count(), 0)

    # Testando atualização da imagem e banco após imagem processada voltar
    def test_update_processing_imagem(self) -> None:
        print(' [*] Teste de atualização banco pós processamento')
        imagem = Imagem.objects.create(arquivo=self.caminho_imagem_teste)

        # Converte a imagem para base64 e prepara o envio
        with open(self.caminho_imagem_teste, 'rb') as f:
            imagem_base64 = base64.b64encode(f.read()).decode('utf-8')
        message = {'id': int(imagem.id), 'caminho': str(imagem.arquivo), 'arquivo': imagem_base64}

        # Chama a função do script para atualizar o banco dizendo que o processamento foi finalizado
        # e obtem o resultado no banco
        ConsumerResults.atualiza_imagem(json.dumps(message))
        imagem = Imagem.objects.get(pk=imagem.id)

        self.assertEqual(imagem.status_processamento, 'Finalizada')
