from rest_framework import serializers

from reporta_baches_api.domain.user.models import User, Empresa
from django.contrib.auth.models import Group


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Empresa
        fields = ['id','empresa']
        

class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    empresa = serializers.CharField(source = "empresa.empresa", read_only=True)

    class Meta: 
        model = User
        fields = ['id','name','email','password','roles','empresa','numero_empleado','telefono']
        
        extra_kwargs = {
            'password':{'write_only':True},
            'fullName':{'read_only':True},
            'id':{'read_only':True}
        }  

    def get_roles(self, obj):
        # Obtener los roles del usuario
        roles = obj.groups.all()
        return [role.name for role in roles]
         
   
         