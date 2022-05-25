from curses.ascii import EM
from django.contrib import admin

from .models import Email

# Register your models here.
admin.site.register(Email)