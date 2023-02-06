# Generated by Django 4.1.6 on 2023-02-03 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Imagem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arquivo', models.ImageField(upload_to='imagens/')),
                ('data_upload', models.DateTimeField(auto_now_add=True)),
                ('status_processamento', models.CharField(default='Pendente', max_length=50)),
            ],
        ),
    ]