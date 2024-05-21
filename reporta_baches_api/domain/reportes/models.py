from django.db import models
from decimal import Decimal
import uuid
from uuid import UUID
from  dataclasses import dataclass
from reporta_baches_api.lib.django import custom_models 
from django.conf import settings



@dataclass
class ReporteCiudadanoBaseParams:
    user: UUID
    latitud: Decimal
    longitud: Decimal
    num_ext: int
    num_int: int
    cp: str
    descripcion: str
    referencia_adicional: str
    direccion: UUID
    modo:str
    #prioridad: UUID

@dataclass
class ReporteTrabajadorBaseParams:
    user: UUID
    ancho: Decimal
    profundidad: Decimal
    prioridad: UUID
    tipo_bache: UUID
    estado_reporte: UUID
    latitud: Decimal
    longitud: Decimal
    cp: str
    direccion: UUID
    modo: str


#TODO llenar calles y alcaldías
class Alcaldia(models.Model):
    id = models.UUIDField(primary_key = True, editable = False,  default=uuid.uuid4)
    alcaldia = models.CharField(max_length = 30)

class Calle(models.Model):
    id = models.UUIDField(primary_key = True, editable = False, default=uuid.uuid4)
    calle = models.CharField(max_length = 50) 
    alcaldia = models.ForeignKey(Alcaldia, on_delete = models.CASCADE)


class ReporteCiudadano(custom_models.DatedModel): 
    id = models.UUIDField(primary_key=True, editable=False,  default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True)
    latitud = models.DecimalField(max_digits = 23, decimal_places =7 )
    longitud =  models.DecimalField(max_digits = 23, decimal_places =7 )
    num_ext = models.IntegerField(null=True)
    num_int = models.IntegerField(null=True)
    cp = models.IntegerField(max_length = 5)
    descripcion = models.CharField(max_length = 300,null=True, blank = True)
    referencia_adicional = models.CharField(max_length = 200, null=True, blank=True)
    direccion = models.ForeignKey(Calle, on_delete = models.DO_NOTHING)
    valido = models.BooleanField(default=False)
    modo = models.CharField(max_length=20, default="Manual")


class Prioridad(models.Model):
    ALTA = 'alta'
    MEDIA = 'media'
    BAJA = 'baja'

    OPCIONES_PRIORIDAD = [
        (ALTA, 'Alta'),
        (MEDIA, 'Media'),
        (BAJA, 'Baja'),
    ]
    id = models.UUIDField(primary_key=True, editable=False,  default=uuid.uuid4)
    prioridad = models.CharField(max_length = 30, choices = OPCIONES_PRIORIDAD)

class TipoBache(models.Model):
    id = models.UUIDField(primary_key=True, editable=False,  default=uuid.uuid4)
    tipo = models.CharField(max_length=20)

class EstadoReporte(models.Model):
    id = models.UUIDField(primary_key=True, editable=False,  default=uuid.uuid4)
    estado = models.CharField(max_length=20)

class ReporteTrabajador(custom_models.DatedModel):
    id = models.UUIDField(primary_key=True, editable=False,  default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True)
    ancho = models.DecimalField(max_digits =6, decimal_places =2)
    profundidad = models.DecimalField(max_digits =6, decimal_places =2)

    prioridad = models.ForeignKey(Prioridad, on_delete = models.DO_NOTHING)
    tipo_bache = models.ForeignKey(TipoBache, on_delete = models.DO_NOTHING)
    estado_reporte = models.ForeignKey(EstadoReporte, on_delete = models.DO_NOTHING)

    latitud = models.DecimalField(max_digits = 23, decimal_places =7 )
    longitud =  models.DecimalField(max_digits = 23, decimal_places =7 )
    direccion = models.ForeignKey(Calle, on_delete = models.DO_NOTHING,null=True)
    cp = models.IntegerField(max_length = 5, default=0)
    valido = models.BooleanField(default=False)
    modo = models.CharField(max_length=20, default="Manual")



class ReporteCiudadanoFactory:
    @staticmethod
    def build_entity(base_params: ReporteCiudadanoBaseParams) -> ReporteCiudadano:
        return ReporteCiudadano.objects.create(
            id=uuid.uuid4(),
            user_id=base_params.user,
            latitud=base_params.latitud,
            longitud=base_params.longitud,
            num_ext=base_params.num_ext,
            num_int=base_params.num_int,
            cp=base_params.cp,
            descripcion=base_params.descripcion,
            referencia_adicional=base_params.referencia_adicional,
            direccion_id=base_params.direccion,
            modo = base_params.modo
            #prioridad_id=base_params.prioridad
        )

class ReporteTrabajadorFactory:
    @staticmethod
    def build_entity(base_params: ReporteTrabajadorBaseParams) -> ReporteTrabajador:
        return ReporteTrabajador.objects.create(
            id=uuid.uuid4(),
            user_id=base_params.user,
            ancho=base_params.ancho,
            profundidad=base_params.profundidad,
            prioridad_id=base_params.prioridad,
            tipo_bache_id=base_params.tipo_bache,
            estado_reporte_id=base_params.estado_reporte,
            latitud=base_params.latitud,
            longitud=base_params.longitud,
            cp = base_params.cp,
            direccion_id=base_params.direccion,
            modo = base_params.modo
        )