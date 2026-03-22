from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Modelo de usuario personalizado para SIZU."""
    sizu_points = models.IntegerField(default=0, help_text="Puntos acumulados por el estudiante")