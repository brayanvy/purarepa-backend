from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    ROLE = (('CLIENT', 'Cliente'), ('ADMIN', 'Administrador'))
    role = models.CharField(max_length=10, choices=ROLE, default='CLIENT')
    phone = models.CharField(max_length=20, blank=True)