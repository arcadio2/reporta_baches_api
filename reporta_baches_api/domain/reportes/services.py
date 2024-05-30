from typing import Type, List, Dict
from .models import ReporteCiudadano, ReporteTrabajador, ReporteTiempoReal
from .models import ReporteCiudadanoFactory, ReporteTrabajadorFactory, ReporteTiempoRealFactory
from .models import ReporteCiudadanoBaseParams, ReporteTrabajadorBaseParams, ReporteTiempoRealBaseParams
from django.db.models.manager import BaseManager

class ReportesService:
     
    """ def __init__(self, log: AttributeLogger):
        self.log = log """

    def get_reporte_ciudadano_factory(self) -> Type[ReporteCiudadanoFactory]:
        return ReporteCiudadanoFactory
    
    def get_reporte_trabajador_factory(self) -> Type[ReporteTrabajadorFactory]:
        return ReporteTrabajadorFactory

    def get_reporte_tiempoReal_factory(self) -> Type[ReporteTiempoRealFactory]:
        return ReporteTiempoRealFactory
    
    def get_reporte_ciudadano_repo(self) -> BaseManager[ReporteCiudadano]:
        return ReporteCiudadano.objects
    
    def get_reporte_trabajador_repo(self) -> BaseManager[ReporteTrabajador]:
        return ReporteTrabajador.objects

    def get_reporte_tiempo_real_repo(self) -> BaseManager[ReporteTiempoReal]:
        return ReporteTiempoReal.objects
    
    def create_reporte_ciudadano(
            self, 
            base_params: ReporteCiudadanoBaseParams) -> ReporteCiudadano:
        
        instance = self.get_reporte_ciudadano_factory().build_entity(base_params=base_params)
        instance.save()
        return instance
    
    def create_reporte_trabajador(
            self, 
            base_params: ReporteTrabajadorBaseParams) -> ReporteTrabajador:
        
        instance = self.get_reporte_trabajador_factory().build_entity(base_params=base_params)
        instance.save()
        return instance
    
    def create_reporte_tiempo_real(
            self, 
            base_params: ReporteTiempoRealBaseParams) -> ReporteTiempoReal:
        
        instance = self.get_reporte_tiempoReal_factory().build_entity(base_params=base_params)
        instance.save()
        return instance
    
    def get_instance_as_dict(self, instance) -> Dict:
        data = {}
        fields = instance._meta.fields
        for field in fields:
            key = field.name
            value = getattr(instance, key)
            data[key] = value
        return data
    
    def get_instances_as_dict(self, instances: List) -> List[Dict]:
        data = []
        for instance in instances:
            instance_dict = self.get_instance_as_dict(instance=instance)
            data.append(instance_dict)
        return data
