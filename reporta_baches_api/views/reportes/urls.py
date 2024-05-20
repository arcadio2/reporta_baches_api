from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from .views import ReportesTrabajador, ReportesCiudadanos, VisualizarImagen
from rest_framework import routers

routers = routers.DefaultRouter()

routers.register('trabajador',ReportesTrabajador,'trbajador')
routers.register('ciudadano',ReportesCiudadanos,'ciudadano')
routers.register('imagenes',VisualizarImagen,'imagenes')


urlpatterns = [
    path('',include(routers.urls)),

    path('docs/', include_docs_urls(title="USER API"))
]