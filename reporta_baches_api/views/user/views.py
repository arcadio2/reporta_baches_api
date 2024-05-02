from rest_framework import viewsets, views, permissions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from datetime import datetime, timedelta

from rest_framework import status

from reporta_baches_api.domain.user.models import User, Empresa
from django.contrib.auth.models import Group

import jwt
from reporta_baches_api.views.user.serializers import UserSerializer, EmpresaSerializer
from reporta_baches_api.lib.django.custom_views import CreateLisViewSet
from reporta_baches_api.lib.errors.response_errors import ResponseError
from rest_framework.decorators import action


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer 


class Register(CreateLisViewSet): 
    serializer_class = UserSerializer

    def get_queryset(self):
        return super().get_queryset()
    def get_serializer_class(self):
        if self.action == "create":
            return UserSerializer
        
    #@action(methods=["post"],detail=False)
    def create(self, request):
        data = request.data
        print(data)
        serializer = self.get_serializer(data=data)
        if(serializer.is_valid()):
            print("Es valido xd")
            user = serializer.save() 
            
            roles = request.data.get('roles', ["ciudadano"])
            for role_name in roles:
                try:
                    role = Group.objects.get(name=role_name)
                    user.groups.add(role)
                    if role_name == "trabajador":
                        empresa = request.data.get('empresa', None)
                        if empresa:
                            try:
                                empresa = Empresa.objects.get(empresa=empresa)
                                user.empresa = empresa
                                user.save()
                            except Empresa.DoesNotExist:
                                pass
                except Group.DoesNotExist:
                    pass
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else: 
            print("No es valido")
        return ResponseError.build_single_error(
                status.HTTP_400_BAD_REQUEST,
                "serializer-error-exception", 
                f"{serializer.errors}"
            ).get_response()


class LoginView(views.APIView):  
    def post(self, request):
        print("Entra aquí")
        
        email = request.data["email"]
        password = request.data["password"]
        #encontrar el email
        user = User.objects.filter(email=email).first()

        if user is None: 
            raise AuthenticationFailed("User not found")
        

        print(user.password, password)
        if not password == user.password:
            raise AuthenticationFailed("Incorrect password")
        
        payload = {
            'id':str(user.id),
            'name':user.name,
            'exp':datetime.now() +timedelta(days=60),
            'iat': datetime.now() 
        }
        token = jwt.encode(payload,'secret',algorithm="HS256")

        user_serializer = UserSerializer(user)
        

        response = Response()
        response.set_cookie(key='jwt',value=token, httponly=True)
        response.data={
            'message': 'success',
            'jwt':token,
            'user':user_serializer.data
        }
    
        return response

class EmpresasView(views.APIView):
    def get(self, request):
        empresas = Empresa.objects.all()
        serializer = EmpresaSerializer(empresas, many=True)
        print(serializer.data)
        response = Response()
        response.data={
            'message': 'success',
            'empresas':serializer.data
        }
        return response

class CheckAuthStatusView(views.APIView):
    def get(self, request):
        if 'Authorization' not in request.headers:
            raise AuthenticationFailed("El encabezado 'Authorization' no está presente en la solicitud")
        
        auth_header = request.headers['Authorization']
        
        
        try:
            if not auth_header.startswith('Bearer '):
                raise AuthenticationFailed("El token Bearer no está presente en el encabezado 'Authorization'")
            # Decodificar el token JWT
            jwt_token = auth_header.split('Bearer ')[1]
            payload = jwt.decode(jwt_token, 'secret', algorithms=["HS256"])
            user_id = payload['id']
            # Buscar al usuario en la base de datos
            user = User.objects.get(id=user_id)
            
            # Serializar el usuario para enviarlo como respuesta
            user_serializer = UserSerializer(user)
            
            # Devolver la respuesta con el usuario autenticado
            return Response({
                'authenticated': True,
                'jwt': jwt_token,
                'user': user_serializer.data
            })
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("El token JWT ha expirado")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Token JWT inválido")
        except User.DoesNotExist:
            raise AuthenticationFailed("Usuario asociado al token no encontrado")

class LogoutView(views.APIView):
    def post(self, request): 
        #payload = validate_token(request)
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            "message":"success, logout"
        }
        return response