# Generated by Django 3.2.19 on 2024-05-10 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reportes', '0005_auto_20240502_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='reporteciudadano',
            name='valido',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='reportetrabajador',
            name='valido',
            field=models.BooleanField(default=False),
        ),
    ]