from datetime import datetime
from  dataclasses import dataclass

from django.db import models


class DatedModel(models.Model):

    created_at = models.DateTimeField(auto_now_add = True)
    modified_at = models.DateTimeField(auto_now = True)


    class Meta:
        abstract = True

@dataclass(frozen=True)
class ModelDates():
    created_at:datetime
    modified_at:datetime