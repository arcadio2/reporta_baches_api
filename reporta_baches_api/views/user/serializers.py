from rest_framework import serializers

from reporta_baches_api.domain.user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = ['id','name','email','password', 'second_name','m_last_name','p_last_name'] 

        
        extra_kwargs = {
            'password':{'write_only':True},
            'id':{'read_only':True}
        }  
 
         
    """Esta función es un intermediario entre el view y el model"""
    """def create(self,validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance"""
         