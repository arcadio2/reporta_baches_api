# Generated by Django 3.2.19 on 2024-05-09 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagenesciudadano',
            name='image',
        ),
        migrations.RemoveField(
            model_name='imagenestrabajador',
            name='image',
        ),
        migrations.AddField(
            model_name='imagenesciudadano',
            name='image_antes',
            field=models.ImageField(default=None, upload_to='imagenes_automatico/antes/'),
        ),
        migrations.AddField(
            model_name='imagenesciudadano',
            name='image_despues',
            field=models.ImageField(default=None, upload_to='imagenes_automatico/despues/'),
        ),
        migrations.AddField(
            model_name='imagenestrabajador',
            name='image_antes',
            field=models.ImageField(default=None, upload_to='imagenes_manual/antes/'),
        ),
        migrations.AddField(
            model_name='imagenestrabajador',
            name='image_despues',
            field=models.ImageField(default=None, upload_to='imagenes_manual/despues/'),
        ),
        migrations.AddField(
            model_name='imagenestrabajador',
            name='valido',
            field=models.BooleanField(default=False),
        ),
    ]
