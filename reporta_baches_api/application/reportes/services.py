import os 
import numpy as np
import cv2
from reporta_baches_api.domain.reportes.models import(
    Calle, 
    Alcaldia,
)


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
            longitud=data['longitud'],
            cp = data['cp'],
            direccion=data['direccion']
        )

        return self.reportes_service.create_reporte_trabajador(params)

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
        reporte = self.reportes_service.create_reporte_ciudadano(params)
        return reporte
    

    def create_direction_if_not_exist(self,calle, alcaldia):
        if not Alcaldia.objects.filter(alcaldia = alcaldia):
            alcaldia_repostory = Alcaldia.objects.create(alcaldia = alcaldia)
            print("Se crea alcaldia", alcaldia_repostory)
            if not Calle.objects.filter(calle = calle):
                Calle.objects.create(calle = calle, alcaldia = alcaldia_repostory)

        if Alcaldia.objects.filter(alcaldia = alcaldia): 
            alcaldia_repostory = Alcaldia.objects.filter(alcaldia = alcaldia).first()
            if not Calle.objects.filter(calle = calle):
                Calle.objects.create(calle = calle, alcaldia = alcaldia_repostory)
    
        # Función para aplicar el filtro de nitidez
    def aplicar_nitidez(self, imagen):
        # Definir un kernel de nitidez
        kernel = np.array([[-1, -1, -1],
                        [-1,  9, -1],
                        [-1, -1, -1]])

        # Aplicar el kernel a la imagen
        imagen_nitida = cv2.filter2D(imagen, -1, kernel)
        return imagen_nitida

    # Filtro para estandarizar el contraste y brillo de la imagen
    def filtroContrasteBrillo(self, imagen):
        alpha = 1  # Factor de contraste
        beta = -10  # Factor de brillo
        imagen_ajustada = cv2.convertScaleAbs(imagen, alpha=alpha, beta=beta)
        return imagen_ajustada

    def preprocess_image(self, image):

        imagen_nitida = self.aplicar_nitidez(image)
        imagen_contraste = self.filtroContrasteBrillo(imagen_nitida)

        return imagen_contraste