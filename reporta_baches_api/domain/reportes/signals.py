
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

@receiver(post_migrate)
def create_default(sender, **kwargs):
    Prioridad = apps.get_model('reportes', 'Prioridad')  
    if not Prioridad.objects.filter(prioridad='Alta').exists():
        Prioridad.objects.create(prioridad='Alta')
    if not Prioridad.objects.filter(prioridad='Media').exists():
        Prioridad.objects.create(prioridad='Media')
    if not Prioridad.objects.filter(prioridad='Baja').exists():
        Prioridad.objects.create(prioridad='Baja')
    
    EstadoReporte = apps.get_model('reportes','EstadoReporte')
    if not EstadoReporte.objects.filter(estado = "Enviado"):
        EstadoReporte.objects.create(estado = "Enviado")

    TipoBache =  apps.get_model('reportes','TipoBache')
    if not TipoBache.objects.filter(tipo = "grieta cocodrilo"): 
        TipoBache.objects.create(tipo = "grieta cocodrilo")

    Alcaldia = apps.get_model('reportes','Alcaldia')
    if not Alcaldia.objects.filter(alcaldia = "Cuauhtémoc"):
        alcaldia = Alcaldia.objects.create(alcaldia = "Cuauhtémoc")
        Calle = apps.get_model('reportes','Calle')
        if not Calle.objects.filter(calle = 'Madero'):
            Calle.objects.create(calle = 'Madero', alcaldia = alcaldia)
    
    
    