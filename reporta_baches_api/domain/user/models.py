from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from reporta_baches_api.lib.django import custom_models


from dataclasses import dataclass
from email.policy import default
import json

# django import
import uuid
from django.db import models




@dataclass(frozen=True)
class UserId:
    value: uuid.UUID


@dataclass
class UserBaseParams: 
    name:str
    id:uuid.UUID
    second_name:str
    m_last_name:str
    p_last_name:str
    email:str
    email_code:str
    password:str
    

class Empresa(custom_models.DatedModel):
    id = models.UUIDField(primary_key=True, editable=False,  default=uuid.uuid4)
    empresa = models.CharField(max_length=255)

class User(AbstractUser):

    id = models.UUIDField(primary_key=True, editable=False,  default=uuid.uuid4)
    name = models.CharField(max_length=255)

    numero_empleado = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, unique=True)

    empresa = models.ForeignKey(Empresa, on_delete = models.DO_NOTHING, null=True, blank=True)

    telefono = models.CharField(max_length=20, help_text='Formato: +525537048075', null=True, blank=True)  
    
    email_code = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=255)
    username = None

    USERNAME_FIELD =  "email"
    REQUIRED_FIELDS = []
    

class UserFactory:
    @staticmethod
    def build_entity(
        base_params: UserBaseParams, 
    ) -> User:
        return User(
                name=base_params.name,
                email=base_params.email,
                email_code=base_params.email_code,
                password=base_params.password
            )

    @classmethod
    def build_entity_with_id(
        cls,
        user_id: UserId,
        base_params: UserBaseParams,
    ) -> User:
        user_id = UserId(uuid.uuid4())
        return cls.build_entity(
            id=user_id,
            base_params = base_params
        )