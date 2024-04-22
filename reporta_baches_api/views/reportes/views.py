from typing import Any
from reporta_baches_api.lib.django.custom_views import CreateLisViewSet
from reporta_baches_api.lib.errors.response_errors import ResponseError
from rest_framework.decorators import action
from reporta_baches_api.decorators.user_decorators import token_required
from reporta_baches_api.domain.reportes.models import(
    ReporteTrabajador,
    TipoBache,
    EstadoReporte, 
    Prioridad,
    ReporteCiudadano,
    Calle, 
    Alcaldia
)
from django.utils.decorators import method_decorator

from reporta_baches_api.views.reportes.serializers import ReporteCiudadanoSerializer, ReporteTrabajadorSerializer
from reporta_baches_api.application.reportes.services import  ReportesAppServices
from reporta_baches_api.domain.reportes.services import ReportesService
from rest_framework import status
from rest_framework.response import Response


class ReportesTrabajador(CreateLisViewSet): 

    """ def __init__(self ) :
        self.reportes_services = ReportesService() """

    serializer_class = ReporteTrabajadorSerializer
    model = ReporteTrabajador

    
    def get_queryset(self):
        reportes_trabajador = ReportesService()
        #query_set =  super().get_queryset()
        return ReporteTrabajador.objects.all()
    
    def get_serializer_class(self):
        if self.action == "create":
            return ReporteTrabajadorSerializer
        
     
    @method_decorator(token_required)
    def create(self, request, payload): 
        data = request.data
        serializer = self.get_serializer(data=data)
        if(serializer.is_valid()):
            tipo_bache = TipoBache.objects.filter(tipo = data.get("tipo_bache")).first()
            estado_reporte = EstadoReporte.objects.filter(estado = data.get("estado_reporte")).first()
            prioridad = Prioridad.objects.filter(prioridad = data.get("prioridad")).first()
            reporte = data.copy()
            reporte["tipo_bache"] = tipo_bache.id
            reporte["estado_reporte"] = estado_reporte.id
            reporte["prioridad"] = prioridad.id
            
            reportesApp = ReportesAppServices()

            reportesApp.create_reporte_trabajador_from_dict(reporte)

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
            reportes_user = reportes_services.get_reporte_trabajador_repo().filter(user_id = "15a245db03ad43dba2640dc7f5b2b88b")
        except:
            print("Error") 

            
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
        
     
    #@method_decorator(token_required)
    def create(self, request, payload=None): 
        data = request.data
        serializer = self.get_serializer(data=data)
        if(serializer.is_valid()):
            
            reporte = data.copy()

            reportes_service = ReportesService()
            
            direccion = Calle.objects.filter(
                calle=reporte["direccion"], 
                alcaldia__alcaldia = reporte["alcaldia"]
            ).first()


            reporte["direccion"] = direccion.id
            del reporte["alcaldia"]
            print(reporte)

            reportesApp = ReportesAppServices()

            reportesApp.create_reporte_ciudadano_from_dict(reporte)

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
            reportes_user = reportes_services.get_reporte_ciudadano_repo().filter(user_id = "15a245db03ad43dba2640dc7f5b2b88b")
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
        

    

    