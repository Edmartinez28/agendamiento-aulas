from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Laboratorio)
admin.site.register(Estacion)
admin.site.register(TimeSlot)
admin.site.register(Reserva)

admin.site.register(Programa)
admin.site.register(EstacionPrograma)
admin.site.register(Carrera)
admin.site.register(Ciclo)
admin.site.register(Paralelo)

admin.site.register(Correo)
admin.site.register(Parametro)
admin.site.register(ImagenLaboratorio)