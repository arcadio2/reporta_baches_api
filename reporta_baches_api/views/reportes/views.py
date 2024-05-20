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
    Alcaldia,
)
from django.utils.decorators import method_decorator
from rest_framework.views import APIView

from reporta_baches_api.views.reportes.serializers import ReporteCiudadanoSerializer, ReporteTrabajadorSerializer, ImagenesTrabajadorSerializer, ImagenesCiudadanoSerializer
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
# Importando el modelo
#PATH_TO_SAVED_MODEL="/home/bruno-rg/reporta_baches_api/mobilenet/saved_model"
PATH_TO_SAVED_MODEL = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../mobilenet/saved_model"))
print('Loading model... \n', end='')
# Load saved model and build the detection function
detect_fn=tf.saved_model.load(PATH_TO_SAVED_MODEL)
print('Done!')

#Loading the label_map
category_index=label_map_util.create_category_index_from_labelmap(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../label_map.pbtxt")),use_display_name=True)

def load_image_into_numpy_array(path):
    return np.array(Image.open(path))

# ==================================================

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
            reporte_valido = False
            for image in images:
                #ImagenesTrabajador.objects.create(image_antes=image, reporte=reporte)
                print('Ejecutando inferencia... ')
                
                image_np = load_image_into_numpy_array(image)
                image_np = reportesApp.preprocess_image(image_np)
                # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
                input_tensor = tf.convert_to_tensor(image_np)
                # The model expects a batch of images, so add an axis with `tf.newaxis`.
                input_tensor = input_tensor[tf.newaxis, ...]

                detections = detect_fn(input_tensor)

                # All outputs are batches tensors.
                # Convert to numpy arrays, and take index [0] to remove the batch dimension.
                # We're only interested in the first num_detections.
                num_detections = int(detections.pop('num_detections'))
                detections = {key: value[0, :num_detections].numpy()
                            for key, value in detections.items()}
                detections['num_detections'] = num_detections

                # detection_classes should be ints.
                detections['detection_classes'] = detections['detection_classes'].astype(np.int64)


                image_np_with_detections = image_np.copy()

                viz_utils.visualize_boxes_and_labels_on_image_array(
                    image_np_with_detections,
                    detections['detection_boxes'],
                    detections['detection_classes'],
                    detections['detection_scores'],
                    category_index,
                    use_normalized_coordinates=True,
                    max_boxes_to_draw=200,
                    min_score_thresh=.4, # Adjust this value to set the minimum probability boxes to be classified as True
                    agnostic_mode=False)
                
                validacion = not (image_np_with_detections == image_np).all()
                if(validacion): 
                    reporte.valido = True


                img_io = io.BytesIO()
                processed_image = Image.fromarray(image_np_with_detections)
                processed_image.save(img_io, format='JPEG')
                img_io.seek(0)
                img_file = InMemoryUploadedFile(img_io, None, 'processed_image.jpg', 'image/jpeg', img_io.tell(), None)
                ImagenesTrabajador.objects.create(image_antes=image, image_despues=img_file, valido=validacion ,reporte=reporte)
            
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
                print('Ejecutando inferencia... ')
                
                image_np = load_image_into_numpy_array(image)
                image_np = reportesApp.preprocess_image(image_np)
                # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
                input_tensor = tf.convert_to_tensor(image_np)
                # The model expects a batch of images, so add an axis with `tf.newaxis`.
                input_tensor = input_tensor[tf.newaxis, ...]

                detections = detect_fn(input_tensor)

                # All outputs are batches tensors.
                # Convert to numpy arrays, and take index [0] to remove the batch dimension.
                # We're only interested in the first num_detections.
                num_detections = int(detections.pop('num_detections'))
                detections = {key: value[0, :num_detections].numpy()
                            for key, value in detections.items()}
                detections['num_detections'] = num_detections

                # detection_classes should be ints.
                detections['detection_classes'] = detections['detection_classes'].astype(np.int64)


                image_np_with_detections = image_np.copy()

                viz_utils.visualize_boxes_and_labels_on_image_array(
                    image_np_with_detections,
                    detections['detection_boxes'],
                    detections['detection_classes'],
                    detections['detection_scores'],
                    category_index,
                    use_normalized_coordinates=True,
                    max_boxes_to_draw=200,
                    min_score_thresh=.4, # Adjust this value to set the minimum probability boxes to be classified as True
                    agnostic_mode=False)
                
                validacion = not (image_np_with_detections == image_np).all()
                if(validacion): 
                    reporte_ciudadano.valido = True


                img_io = io.BytesIO()
                processed_image = Image.fromarray(image_np_with_detections)
                processed_image.save(img_io, format='JPEG')
                img_io.seek(0)
                img_file = InMemoryUploadedFile(img_io, None, 'processed_image.jpg', 'image/jpeg', img_io.tell(), None)
                ImagenesCiudadano.objects.create(image_antes=image, image_despues=img_file, valido=validacion ,reporte=reporte_ciudadano)
            else:
                print("Error de serializacion")
            serializer = ReporteCiudadanoSerializer(reporte_ciudadano)
            reporte_ciudadano.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


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
            reportes_user = reportes_services.get_reporte_ciudadano_repo().filter(user_id = payload["id"])
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

