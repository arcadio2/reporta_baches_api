from rest_framework import serializers

from reporta_baches_api.domain.user.models import User
from django.contrib.auth.models import Group


class UserSerializer(serializers.ModelSerializer):
    fullName = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    class Meta: 
        model = User
        fields = ['id','name','email','password', 'second_name','m_last_name','p_last_name','fullName','roles'] 

        
        extra_kwargs = {
            'password':{'write_only':True},
            'fullName':{'read_only':True},
            'id':{'read_only':True}
        }  
    def get_fullName(self, obj):
        # Concatena el nombre y los apellidos
        return f"{obj.name} {obj.m_last_name} {obj.p_last_name}"
    def get_roles(self, obj):
        # Obtener los roles del usuario
        roles = obj.groups.all()
        return [role.name for role in roles]
         
   
         