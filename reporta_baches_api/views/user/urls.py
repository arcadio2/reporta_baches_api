from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from .views import LoginView, RegisterViewSet, Register, CheckAuthStatusView, EmpresasView
from rest_framework import routers

routers = routers.DefaultRouter()

routers.register('register',Register,'register')


urlpatterns = [
    path('',include(routers.urls)),
    path('login',LoginView.as_view()),
    path('empresas/', EmpresasView.as_view(), name='empresas'),
    path('checkauthstatus', CheckAuthStatusView.as_view()),
    #path('login',LoginView.as_view()),
    #path('logout',LogoutView.as_view()),
    path('docs/', include_docs_urls(title="USER API"))
   
]