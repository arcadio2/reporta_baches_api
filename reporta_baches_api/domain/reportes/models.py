from django.db import models
from decimal import Decimal
import uuid
from  dataclasses import dataclass
from reporta_baches_api.lib.django import custom_models 
from django.conf import settings

#TODO llenar calles y alcaldías
class Alcaldia(models.Model):
    id = models.UUIDField(primary_key = True, editable = False)
    alcaldia = models.CharField(max_length = 30)

class Calle(models.Model):
    id = models.UUIDField(primary_key = True, editable = False)
    calle = models.CharField(max_length = 50) 
    alcaldia = models.ForeignKey(Alcaldia, on_delete = models.CASCADE)


class ReporteCiudadano(custom_models.DatedModel): 
    id = models.UUIDField(primary_key=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True)
    latitud = models.DecimalField(max_digits = 23, decimal_places =4 )
    longitud =  models.DecimalField(max_digits = 23, decimal_places =4 )
    num_ext = models.IntegerField()
    num_int = models.IntegerField()
    cp = models.IntegerField(max_length = 5)
    descripcion = models.CharField(max_length = 300)
    referencia_adicional = models.CharField(max_length = 200)
    direccion = models.ForeignKey(Calle, on_delete = models.DO_NOTHING)


class Prioridad(models.Model):
    ALTA = 'alta'
    MEDIA = 'media'
    BAJA = 'baja'

    OPCIONES_PRIORIDAD = [
        (ALTA, 'Alta'),
        (MEDIA, 'Media'),
        (BAJA, 'Baja'),
    ]
    id = models.UUIDField(primary_key=True, editable=False)
    prioridad = models.CharField(max_length = 30, choices = OPCIONES_PRIORIDAD)

class TipoBache(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    tipo = models.CharField(max_length=20)

class EstadoReporte(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    estado = models.CharField(max_length=20)

class ReporteTrabajador(custom_models.DatedModel):
    id = models.UUIDField(primary_key=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True)
    ancho = models.DecimalField(max_digits =6, decimal_places =2)
    profundidad = models.DecimalField(max_digits =6, decimal_places =2)

    prioridad = models.ForeignKey(Prioridad, on_delete = models.DO_NOTHING)
    tipo_bache = models.ForeignKey(TipoBache, on_delete = models.DO_NOTHING)
    estado_reporte = models.ForeignKey(EstadoReporte, on_delete = models.DO_NOTHING)

    latitud = models.DecimalField(max_digits = 23, decimal_places =4 )
    longitud =  models.DecimalField(max_digits = 23, decimal_places =4 )