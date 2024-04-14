from rest_framework import viewsets, views, permissions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from datetime import datetime 
from rest_framework import status

from reporta_baches_api.domain.user.models import User
import jwt
from reporta_baches_api.views.user.serializers import UserSerializer
from reporta_baches_api.lib.django.custom_views import CreateLisViewSet
from reporta_baches_api.lib.errors.response_errors import ResponseError
from rest_framework.decorators import action


class RegisterViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer 


class Register(CreateLisViewSet): 
    serializer_class = UserSerializer
    def get_serializer_class(self):
        if self.action == "create":
            return UserSerializer
        
    #@action(methods=["post"],detail=False)
    def create(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        if(serializer.is_valid()):
            user = serializer.save() 
            print(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return ResponseError.build_single_error(
                status.HTTP_400_BAD_REQUEST,
                "serializer-error-exception", 
                f"{serializer.errors}"
            ).get_response()


class LoginView(views.APIView):  
    def post(self, request):
        
        email = request.data["email"]
        password = request.data["password"]
        #encontrar el email
        user = User.objects.filter(email=email).first()

        if user is None: 
            raise AuthenticationFailed("User not found")
        
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password")
        
        payload = {
            'id':user.id,
            'name':user.name,
            'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow() 
        }
        token = jwt.encode(payload,'secret',algorithm="HS256")

        response = Response()
        response.set_cookie(key='jwt',value=token, httponly=True)
        response.data={
            'message': 'success',
            'jwt':token
            #'user': UserSerializer(user)
        }
        

        return response

class LogoutView(views.APIView):
    def post(self, request): 
        #payload = validate_token(request)
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            "message":"success, logout"
        }
        return response