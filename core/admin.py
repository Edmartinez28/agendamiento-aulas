from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Laboratorio)
admin.site.register(Estacion)
admin.site.register(TimeSlot)
admin.site.register(Reserva)
