from django.db import models
from reporta_baches_api.lib.django import custom_models
import uuid
from reporta_baches_api.domain.reportes.models import ReporteCiudadano,ReporteTrabajador



# Create your models here.
class ImagenesTrabajador(custom_models.DatedModel):
    id = models.UUIDField(primary_key=True, editable=False,  default=uuid.uuid4)
    image_antes = models.ImageField(upload_to='imagenes_manual/antes/', default=None)
    image_despues = models.ImageField(upload_to='imagenes_manual/despues/', default=None)
    valido = models.BooleanField(default=False)
    reporte = models.ForeignKey(ReporteTrabajador,on_delete=models.CASCADE)



class ImagenesCiudadano(custom_models.DatedModel):
    id = models.UUIDField(primary_key=True, editable=False,  default=uuid.uuid4)
    image_antes = models.ImageField(upload_to='imagenes_automatico/antes/', default=None)
    image_despues = models.ImageField(upload_to='imagenes_automatico/despues/', default=None)
    reporte = models.ForeignKey(ReporteCiudadano,on_delete=models.CASCADE)

