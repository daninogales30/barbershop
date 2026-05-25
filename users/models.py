from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField()
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    foto_perfil = models.ImageField(
        upload_to='perfiles/',
        null=True,
        blank=True,
        default='perfiles/default.png'
    )