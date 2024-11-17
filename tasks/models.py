from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class Fecha(models.Model):
    fecha = models.DateField()

class CustomUser(AbstractUser):
    rol = models.IntegerField(default=0)  # 0 para estudiante, 1 para administrador
