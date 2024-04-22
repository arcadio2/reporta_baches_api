from django.db import models
from reporta_baches_api.lib.django import custom_models
import uuid
from reporta_baches_api.domain.reportes.models import ReporteCiudadano,ReporteTrabajador



# Create your models here.
class ImagenesTrabajador(custom_models.DatedModel):
    id = models.UUIDField(primary_key=True, editable=False,  default=uuid.uuid4)
    image = models.ImageField(upload_to='imagenes/')
    reporte = models.ForeignKey(ReporteTrabajador,on_delete=models.CASCADE)



class ImagenesCiudadano(custom_models.DatedModel):
    id = models.UUIDField(primary_key=True, editable=False,  default=uuid.uuid4)
    image = models.ImageField(upload_to='imagenes/')
    reporte = models.ForeignKey(ReporteCiudadano,on_delete=models.CASCADE)

