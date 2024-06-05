from typing import Any
from reporta_baches_api.lib.django.custom_views import CreateLisViewSet
from reporta_baches_api.lib.errors.response_errors import ResponseError
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from reporta_baches_api.domain.images.models import ImagenesCiudadano, ImagenesTrabajador

from reporta_baches_api.decorators.user_decorators import token_required
from reporta_baches_api.domain.reportes.models import(
    ReporteTrabajador,
    TipoBache,
    EstadoReporte, 
    Prioridad,
    ReporteCiudadano,
    Calle, 
    ReporteTiempoReal,
    Alcaldia,
)
from reporta_baches_api.domain.user.models import User
from django.utils.decorators import method_decorator
from rest_framework.views import APIView

from reporta_baches_api.views.reportes.serializers import ReporteCiudadanoSerializer, ReporteTrabajadorSerializer, ImagenesTrabajadorSerializer, ImagenesCiudadanoSerializer, ReporteTiempoRealSerializer
from reporta_baches_api.application.reportes.services import  ReportesAppServices
from reporta_baches_api.domain.reportes.services import ReportesService
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse
import io
from django.core.files.uploadedfile import InMemoryUploadedFile

#Librerias para modelo
#Loading the saved_model
import tensorflow as tf
import time
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
import random
import matplotlib.pyplot as plt
import os 

# ================== Modelo de IA ==================
# ================== MODO MANUAL ==================
# Importando el modelo
PATH_TO_SAVED_MODEL = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../mobilenet_manual/saved_model"))
print('Loading manual model... \n', end='')
# Load saved model and build the detection function
detect_fn_manual=tf.saved_model.load(PATH_TO_SAVED_MODEL)
print('Done manual!')

#Loading the label_map
category_index_manual=label_map_util.create_category_index_from_labelmap(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../mobilenet_manual/label_map_manual.pbtxt")),use_display_name=True)
# ================== MODO MANUAL ==================
# ================== MODO AUTOMATICO ==================

# Importando el modelo
PATH_TO_SAVED_MODEL_AUTOMATIC = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../mobilenet_automatico/saved_model"))
print('Loading automatic model... \n', end='')
# Load saved model and build the detection function
detect_fn_automatico=tf.saved_model.load(PATH_TO_SAVED_MODEL_AUTOMATIC)
print('Done automatic!')

#Loading the label_map
category_index_automatico=label_map_util.create_category_index_from_labelmap(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../mobilenet_automatico/label_map_automatico.pbtxt")),use_display_name=True)
# ================== MODO AUTOMATICO ==================

def load_image_into_numpy_array(path):
    return np.array(Image.open(path))

# ================== Modelo de IA ==================

class ReportesTrabajador(CreateLisViewSet): 

    serializer_class = ReporteTrabajadorSerializer
    model = ReporteTrabajador
    #parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        reportes_trabajador = ReportesService()
        #query_set =  super().get_queryset()
        return ReporteTrabajador.objects.all()
    
    def get_serializer_class(self):
        if self.action == "create":
            return ReporteTrabajadorSerializer
        
     
    @method_decorator(token_required)
    def create(self, request, payload): 
        images = request.FILES.getlist('images')
        data = dict(request.data)
        #data["images"].
        data = {key: value[0] if isinstance(value, list) else value for key, value in data.items()}
        data['modo'] = data.get('modo', 'manual')
        serializer = self.get_serializer(data=data)
        if(serializer.is_valid()):
            tipo_bache = TipoBache.objects.filter(tipo = data.get("tipo_bache")).first()
            estado_reporte = EstadoReporte.objects.filter(estado = data.get("estado_reporte")).first()
            prioridad = Prioridad.objects.filter(prioridad = data.get("prioridad")).first()
            reporte = data.copy()
            reporte["tipo_bache"] = tipo_bache.id
            reporte["estado_reporte"] = estado_reporte.id
            reporte["prioridad"] = prioridad.id
            reporte["user"] = payload["id"]
            usuario = User.objects.get(id=payload["id"])
            """Add Direction"""
            reportesApp = ReportesAppServices()
            reportesApp.create_direction_if_not_exist(reporte["direccion"],reporte["alcaldia"])
            
            
            direccion = Calle.objects.filter(
                calle=reporte["direccion"], 
                alcaldia__alcaldia = reporte["alcaldia"]
            ).first()



            reporte["direccion"] = direccion.id
            if(reporte["cp"]):
                reporte["cp"] = int(reporte["cp"])

            reporte["user"] = payload["id"]
            del reporte["alcaldia"]
            """END Add direction"""
            
            reportesApp = ReportesAppServices()

            reporte = reportesApp.create_reporte_trabajador_from_dict(reporte)
            print("Reporte", reporte)
            print(data)
            reporte_valido = False
            for image in images:
                #ImagenesTrabajador.objects.create(image_antes=image, reporte=reporte)
                
                image_np = load_image_into_numpy_array(image)
                #image_np = reportesApp.preprocess_image(image_np)
                # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
                input_tensor = tf.convert_to_tensor(image_np)
                # The model expects a batch of images, so add an axis with `tf.newaxis`.
                input_tensor = input_tensor[tf.newaxis, ...]
                
                categories = category_index_manual
                if(data["modo"] == "manual"): 
                    print('Ejecutando inferencia manual... ')
                    detections = detect_fn_manual(input_tensor)
                    categories = category_index_manual 
                
                else: 
                    print('Ejecutando inferencia automatica... ')
                    detections = detect_fn_automatico(input_tensor)
                    categories = category_index_automatico
            
             
                image_np_with_detections = reportesApp.procces_image(detections,categories, image_np.copy())

                validacion = not (image_np_with_detections == image_np).all()
                if(validacion): 
                    reporte.valido = True
                else: 
                    detections = detect_fn_automatico(input_tensor)
                    categories = category_index_automatico
                    image_np_with_detections = reportesApp.procces_image(detections,categories, image_np.copy())
                    validacion = not (image_np_with_detections == image_np).all()
                    if(validacion): 
                        reporte.valido = True


                img_io = io.BytesIO()
                processed_image = Image.fromarray(image_np_with_detections)
                processed_image.save(img_io, format='JPEG')
                img_io.seek(0)
                img_file = InMemoryUploadedFile(img_io, None, 'processed_image.jpg', 'image/jpeg', img_io.tell(), None)
                ImagenesTrabajador.objects.create(image_antes=image, image_despues=img_file, valido=validacion ,reporte=reporte)
            

           
            reportesApp.send_email(user= usuario, reporte = reporte)
            # Agregamos correo                
                
            serializer = ReporteTrabajadorSerializer(reporte)
            reporte.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else: 
            print("ENTRA")
        return ResponseError.build_single_error(
                status.HTTP_400_BAD_REQUEST,
                "serializer-error-exception", 
                f"{serializer.errors}"
            ).get_response()
    
    @method_decorator(token_required)
    @action(methods=["get"],detail=False, url_path="get")
    def get_list_by_user(self, request,payload=None,name="get_list_by_user"):    
        reportes_services = ReportesService()
        reportes_user = None
        id_user = payload["id"]
        try:
            print("XDDDD",id_user)
            reportes_user = reportes_services.get_reporte_trabajador_repo().filter(user_id = id_user).order_by("-created_at")
        except :
            return ResponseError.build_single_error(
                status.HTTP_400_BAD_REQUEST,
                "invalid-id", 
                f"Error"
            ).get_response()

            
        serializer = ReporteTrabajadorSerializer(reportes_user,many=True)
        
        #if(serializer.is_valid()):
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        return ResponseError.build_single_error(
                status.HTTP_204_NO_CONTENT,
                "serializer-error-exception", 
                f"{serializer.errors}"
            ).get_response()
        data = 1 


class ReportesCiudadanos(CreateLisViewSet): 

    """ def __init__(self ) :
        self.reportes_services = ReportesService() """

    serializer_class = ReporteCiudadanoSerializer
    model = ReporteCiudadano

    
    def get_queryset(self):
        reportes_ciudadano = ReporteCiudadano()
        #query_set =  super().get_queryset()
        return ReporteTrabajador.objects.all()
    
    def get_serializer_class(self):
        if self.action == "create":
            return ReporteCiudadanoSerializer
        
     
    @method_decorator(token_required)
    def create(self, request, payload=None): 
        images = request.FILES.getlist('images')
        data = dict(request.data)
        #data["images"].
        data = {key: value[0] if isinstance(value, list) else value for key, value in data.items()}
        data['modo'] = data.get('modo', 'manual')

        print("data",data)
        print("Imagenes", images)
        serializer = self.get_serializer(data=data)


        if(serializer.is_valid()):
            
            reporte = data.copy()

            reportes_service = ReportesService()
            reportesApp = ReportesAppServices()
            reportesApp.create_direction_if_not_exist(reporte["direccion"],reporte["alcaldia"])

            print("Direccion: ",reporte["direccion"], reporte["alcaldia"])
            
            direccion = Calle.objects.filter(
                calle=reporte["direccion"], 
                alcaldia__alcaldia = reporte["alcaldia"]
            ).first()

            print("La direccion es ",direccion.alcaldia.alcaldia, direccion.calle)

            reporte["direccion"] = direccion.id
            if(reporte["cp"]):
                reporte["cp"] = int(reporte["cp"])

            if(reporte["num_int"]):
                reporte["num_int"] = int(reporte["num_int"])

            if(reporte["num_ext"]):
                reporte["num_ext"] = int(reporte["num_ext"])

            reporte["user"] = payload["id"]
            del reporte["alcaldia"]
            print(reporte)


            reporte_ciudadano = reportesApp.create_reporte_ciudadano_from_dict(reporte)
            for image in images:
                #ImagenesTrabajador.objects.create(image_antes=image, reporte=reporte)
                
                
                image_np = load_image_into_numpy_array(image)
                #image_np = reportesApp.preprocess_image(image_np)
                # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
                input_tensor = tf.convert_to_tensor(image_np)
                # The model expects a batch of images, so add an axis with `tf.newaxis`.
                input_tensor = input_tensor[tf.newaxis, ...]

                categories = category_index_manual
                if(data["modo"]== "manual"): 
                    print('Ejecutando inferencia manual... ')
                    detections = detect_fn_manual(input_tensor)
                    categories = category_index_manual 
                else: 
                    print('Ejecutando inferencia automatica... ')
                    detections = detect_fn_automatico(input_tensor)
                    categories = category_index_automatico

                image_np_with_detections = reportesApp.procces_image(detections,categories, image_np.copy())

                validacion = not (image_np_with_detections == image_np).all()
                if(validacion): 
                    reporte.valido = True
                else: 
                    detections = detect_fn_automatico(input_tensor)
                    categories = category_index_automatico
                    image_np_with_detections = reportesApp.procces_image(detections,categories, image_np.copy())
                    validacion = not (image_np_with_detections == image_np).all()
                    if(validacion): 
                        reporte.valido = True


                img_io = io.BytesIO()
                processed_image = Image.fromarray(image_np_with_detections)
                processed_image.save(img_io, format='JPEG')
                img_io.seek(0)
                img_file = InMemoryUploadedFile(img_io, None, 'processed_image.jpg', 'image/jpeg', img_io.tell(), None)
                print("LLEGA ANTES DE CREAR")
                ImagenesCiudadano.objects.create(image_antes=image, image_despues=img_file, valido=validacion ,reporte=reporte_ciudadano)
                print("CREA LA IMAGEN")

            serializer = ReporteCiudadanoSerializer(reporte_ciudadano)
            reporte_ciudadano.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Error de serializacion")


        return ResponseError.build_single_error(
                status.HTTP_400_BAD_REQUEST,
                "serializer-error-exception", 
                f"{serializer.errors}"
            ).get_response()
    
    @method_decorator(token_required)
    @action(methods=["get"],detail=False, url_path="get")
    def get_list_by_user(self, request,payload=None,name="get_list_by_user"):    
        reportes_services = ReportesService()
        try:
            reportes_user = reportes_services.get_reporte_ciudadano_repo().filter(user_id = payload["id"]).order_by("-created_at")
        except:
            print("Error") 

            
        serializer = ReporteCiudadanoSerializer(reportes_user,many=True)
        
        #if(serializer.is_valid()):
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        return ResponseError.build_single_error(
                status.HTTP_204_NO_CONTENT,
                "serializer-error-exception", 
                f"{serializer.errors}"
            ).get_response()
        data = 1 

class ReportesTiempoReal(CreateLisViewSet): 
    serializer_class = ReporteTiempoRealSerializer
    model = ReporteTiempoReal

    
    def get_queryset(self):
        reportes_ciudadano = ReporteTiempoReal()
        #query_set =  super().get_queryset()
        return ReportesTiempoReal.objects.all()
    
    def get_serializer_class(self):
        if self.action == "create":
            return ReporteTiempoRealSerializer
        
    @method_decorator(token_required)
    def create(self, request, payload=None):
        image = request.FILES.getlist('images')[0]
        data = dict(request.data)
        #data["images"].
        data = {key: value[0] if isinstance(value, list) else value for key, value in data.items()}
        ras = ReportesAppServices()
        #data = request.data 
        serializer = self.get_serializer(data=data)
        data["user"] = payload["id"]
        if(data["cp"]):
            data["cp"] = int(data["cp"])
        
        print("Image ", data["cp"], data["longitud"], data["latitud"], data["user"])
        
        if(serializer.is_valid()):
            ras.create_direction_if_not_exist(data["direccion"],data["alcaldia"])

            print("Direccion: ",data["direccion"], data["alcaldia"])
            
            direccion = Calle.objects.filter(
                calle=data["direccion"], 
                alcaldia__alcaldia = data["alcaldia"]
            ).first()

            print("La direccion es ",direccion.alcaldia.alcaldia, direccion.calle)
            data["direccion"] = direccion.id
           
            #image_np = np.array(image, dtype=np.uint8)
            #print(image_np)
            #img_file = InMemoryUploadedFile(img_io, None, 'processed_image.jpg', 'image/jpeg', img_io.tell(), None)
            reporte = ras.create_reporte_tiempo_real_from_dict(data,image)
            print("LLEHA AQUI JEJEJ")
            serializer = ReporteTiempoRealSerializer(reporte)
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Bad request", serializer.errors)
            return ResponseError.build_single_error(
                    status.HTTP_400_BAD_REQUEST,
                    "serializer-error-exception", 
                    f"{serializer.rerors}"
                ).get_response()

    @method_decorator(token_required)
    @action(methods=["get"],detail=False, url_path="get")
    def get_list_by_user(self, request,payload=None,name="get_list_by_user"):    
        reportes_services = ReportesService()
        try:
            reportes_user = reportes_services.get_reporte_tiempo_real_repo().filter(user_id = payload["id"]).order_by("-created_at")
        except:
            print("Error") 
            
        serializer = ReporteTiempoRealSerializer(reportes_user,many=True)
        
        #if(serializer.is_valid()):
        return Response(serializer.data, status=status.HTTP_200_OK)



        
class VisualizarImagen(CreateLisViewSet):
    
    serializer_class = ImagenesTrabajadorSerializer
    model = ImagenesTrabajador
    #parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return ImagenesTrabajador.objects.all()
    
    def get_serializer_class(self):
        
        return ImagenesTrabajadorSerializer
    
    
    def get(self, request):
        return Response(ImagenesTrabajadorSerializer(ImagenesTrabajador.objects.all()).data)
    
    @action(detail=False, methods=['get'], name='get_imagen_antes_trabajador')
    def get_imagen_antes_trabajador(self, request):
        queryparams = request.query_params
        image_id= queryparams["image_id"]
        print(image_id)
        try:
            imagen = ImagenesTrabajador.objects.get(id=image_id)
        except ImagenesTrabajador.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ImagenesTrabajadorSerializer(imagen)
        # Incluir la URL de la imagen en la respuesta JSON
        #data = serializer.data
        #data['image_url'] = imagen.image_despues.url 
        image_content = imagen.image_antes.read()
        content_type = 'image/jpeg'
        return HttpResponse(image_content, content_type=content_type)
    
    @action(detail=False, methods=['get'], name='get_imagen_despues_trabajador')
    def get_imagen_despues_trabajador(self, request):
        queryparams = request.query_params
        image_id= queryparams["image_id"]
        try:
            imagen = ImagenesTrabajador.objects.get(id=image_id)
        except ImagenesTrabajador.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ImagenesTrabajadorSerializer(imagen)
    
        image_content = imagen.image_despues.read()
        content_type = 'image/jpeg'
        return HttpResponse(image_content, content_type=content_type)

    @action(detail=False, methods=['get'], name='get_imagen_antes_ciudadano')
    def get_imagen_antes_ciudadano(self, request):
        queryparams = request.query_params
        image_id= queryparams["image_id"]
        print(image_id)
        try:
            imagen = ImagenesCiudadano.objects.get(id=image_id)
        except ImagenesCiudadano.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ImagenesCiudadanoSerializer(imagen)
        # Incluir la URL de la imagen en la respuesta JSON
        #data = serializer.data
        #data['image_url'] = imagen.image_despues.url 
        image_content = imagen.image_antes.read()
        content_type = 'image/jpeg'
        return HttpResponse(image_content, content_type=content_type)
    
    @action(detail=False, methods=['get'], name='get_imagen_despues_ciudadano')
    def get_imagen_despues_ciudadano(self, request):
        queryparams = request.query_params
        image_id= queryparams["image_id"]
        try:
            imagen = ImagenesCiudadano.objects.get(id=image_id)
        except ImagenesCiudadano.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ImagenesCiudadanoSerializer(imagen)
    
        image_content = imagen.image_despues.read()
        content_type = 'image/jpeg'
        return HttpResponse(image_content, content_type=content_type)

    @action(detail=False, methods=['get'], name='get_imagen_tiempo_real')
    def get_imagen_tiempo_real(self, request):
        queryparams = request.query_params
        image_id= queryparams["image_id"]
        try:
            imagen = ReporteTiempoReal.objects.get(id=image_id)
        except ReporteTiempoReal.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        
    
        image_content = imagen.image.read()
        content_type = 'image/jpeg'
        return HttpResponse(image_content, content_type=content_type)
    
    
    

