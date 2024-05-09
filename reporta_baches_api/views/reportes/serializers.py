from rest_framework import serializers
from reporta_baches_api.domain.reportes.models import ReporteTrabajador, ReporteCiudadano
from reporta_baches_api.domain.reportes.models import Prioridad, TipoBache, EstadoReporte, Calle, Alcaldia
from reporta_baches_api.domain.images.models import ImagenesTrabajador, ImagenesCiudadano

class PrioridadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prioridad
        fields = ['id', 'prioridad']

class TipoBacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoBache
        fields = ['id', 'tipo']

class EstadoReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoReporte
        fields = ['id', 'estado']

class CalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calle
        fields = ['id', 'calle', 'alcaldia']

class AlcaldiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alcaldia
        fields = ['id', 'alcaldia']

class ReporteTrabajadorSerializer(serializers.ModelSerializer):
    prioridad = serializers.CharField(source='prioridad.prioridad')
    tipo_bache = serializers.CharField(source = "tipo_bache.tipo")#TipoBacheSerializer()
    estado_reporte = serializers.CharField(source = "estado_reporte.estado") #EstadoReporteSerializer()
    
    class Meta:
        model = ReporteTrabajador
        fields = ['id', 'created_at', 'user', 'ancho', 'profundidad', 'prioridad', 'tipo_bache', 'estado_reporte', 'latitud', 'longitud']
        extra_kwargs = {
            'id':{'read_only':True},
            'user':{'read_only':True},
            'created_at':{'read_only':True}
        }  
 

class ReporteCiudadanoSerializer(serializers.ModelSerializer):
    direccion = serializers.CharField(source = "direccion.calle")
    alcaldia = serializers.CharField(source = "direccion.alcaldia.alcaldia")
    class Meta:
        model = ReporteCiudadano
        fields = ['id','created_at', 'user', 'latitud', 'longitud', 'num_ext', 'num_int', 'cp', 'descripcion', 'referencia_adicional', 'direccion', 'alcaldia']
        extra_kwargs = {
            'id':{'read_only':True},
            'created_at':{'read_only':True},
            'user':{'read_only':True},
        }  


class ImagenesTrabajadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenesTrabajador
        fields = ['id','image_antes','image_despues','valido']