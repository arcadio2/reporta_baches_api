from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


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
    

class User(AbstractUser):

    id = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    second_name = models.CharField(max_length=150, blank=True, null=True)
    m_last_name = models.CharField(max_length=150, blank=True, null=True)
    p_last_name = models.CharField(max_length=150, blank=True, null=True)

    email = models.CharField(max_length=255, unique=True)
    
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
                second_name=base_params.second_name,
                m_last_name=base_params.m_last_name,
                p_last_name=base_params.p_last_name,
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