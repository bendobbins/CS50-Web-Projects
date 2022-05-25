from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    age = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to=f'{AbstractUser.username}')