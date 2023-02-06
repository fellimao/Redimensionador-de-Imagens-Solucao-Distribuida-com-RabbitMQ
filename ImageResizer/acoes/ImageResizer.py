from PIL import Image
import base64
import io


# Redimensiona a imagem para o tamanho desejado
def ImageResizer(imagem_encoded: str, file_extension: str, altura: int, largura: int) -> str:
    imagem_bytes = base64.b64decode(imagem_encoded)
    imagem = Image.open(io.BytesIO(imagem_bytes))
    imagem_redimensionada = imagem.resize((altura, largura), resample=Image.BICUBIC)
    bytes_buffer = io.BytesIO()

    if (file_extension == '.png'):
        imagem_redimensionada.save(bytes_buffer, 'PNG')
    else:
        imagem_redimensionada.save(bytes_buffer, 'JPEG')

    Imagem_encoded = base64.b64encode(bytes_buffer.getvalue()).decode("utf-8")
    return Imagem_encoded
