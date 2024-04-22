
from reporta_baches_api.domain.reportes.services import ReportesService

from reporta_baches_api.domain.reportes.models import (
    ReporteCiudadanoBaseParams,
    ReporteTrabajadorBaseParams
)


class ReportesAppServices: 
    def __init__(self):
        self.reportes_service = ReportesService()

    def create_reporte_trabajador_from_dict(self, data:dict):

        params = ReporteTrabajadorBaseParams(
            user=data['user'],
            ancho=data['ancho'],
            profundidad=data['profundidad'],
            prioridad=data['prioridad'],
            tipo_bache=data['tipo_bache'],
            estado_reporte=data['estado_reporte'],
            latitud=data['latitud'],
            longitud=data['longitud']
        )

        self.reportes_service.create_reporte_trabajador(params)

    def create_reporte_ciudadano_from_dict(self, data:dict): 

        params = ReporteCiudadanoBaseParams(
          
                user=data['user'],
                latitud=data['latitud'],
                longitud=data['longitud'],
                num_ext=data['num_ext'],
                num_int=data['num_int'],
                cp=data['cp'],
                descripcion=data['descripcion'],
                referencia_adicional=data['referencia_adicional'],
                direccion=data['direccion']
            
        )
        self.reportes_service.create_reporte_ciudadano(params)