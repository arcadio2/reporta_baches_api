from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Crea roles predeterminados'

    def handle(self, *args, **options):
        roles_to_create = ['admin', 'ciudadano','trabajador']  # Lista de roles a crear
        for role_name in roles_to_create:
            _, created = Group.objects.get_or_create(name=role_name)