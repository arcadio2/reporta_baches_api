# Generated by Django 3.2.19 on 2024-04-30 04:37

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_user_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Empresa',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('empresa', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='user',
            name='m_last_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='p_last_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='second_name',
        ),
        migrations.AddField(
            model_name='user',
            name='numero_empleado',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='telefono',
            field=models.CharField(help_text='Formato: +525537048075', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='empresa',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='user.empresa'),
        ),
    ]
