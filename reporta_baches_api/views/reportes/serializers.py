from rest_framework import serializers
from reporta_baches_api.domain.reportes.models import ReporteTrabajador, ReporteCiudadano
from reporta_baches_api.domain.reportes.models import Prioridad, TipoBache, EstadoReporte, Calle, Alcaldia

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
    prioridad = PrioridadSerializer()
    tipo_bache = TipoBacheSerializer()
    estado_reporte = EstadoReporteSerializer()
    class Meta:
        model = ReporteTrabajador
        fields = ['id', 'user', 'ancho', 'profundidad', 'prioridad', 'tipo_bache', 'estado_reporte', 'latitud', 'longitud']

class ReporteCiudadanoSerializer(serializers.ModelSerializer):
    direccion = CalleSerializer()
    class Meta:
        model = ReporteCiudadano
        fields = ['id', 'user', 'latitud', 'longitud', 'num_ext', 'num_int', 'cp', 'descripcion', 'referencia_adicional', 'direccion']
