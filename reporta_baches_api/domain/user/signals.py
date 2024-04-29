""" from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_default(sender, **kwargs):
    roles_to_create = ['admin', 'trabajador','ciudadano']  # Lista de roles a crear
    for role_name in roles_to_create:
        _, created = Group.objects.get_or_create(name=role_name) """