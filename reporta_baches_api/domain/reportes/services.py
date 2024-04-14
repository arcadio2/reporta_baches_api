from typing import Type, List, Dict
from .models import ReporteCiudadano, ReporteTrabajador
from .models import ReporteCiudadanoFactory, ReporteTrabajadorFactory
from .models import ReporteCiudadanoBaseParams, ReporteTrabajadorBaseParams

class ReportesService:
     
    """ def __init__(self, log: AttributeLogger):
        self.log = log """

    def get_reporte_ciudadano_factory(self) -> Type[ReporteCiudadanoFactory]:
        return ReporteCiudadanoFactory
    
    def get_reporte_trabajador_factory(self) -> Type[ReporteTrabajadorFactory]:
        return ReporteTrabajadorFactory
    
    def get_reporte_ciudadano_repo(self) -> Type[ReporteCiudadano]:
        return ReporteCiudadano.objects
    
    def get_reporte_trabajador_repo(self) -> Type[ReporteTrabajador]:
        return ReporteTrabajador.objects
    
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
