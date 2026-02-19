from django.urls import path
from .views import *

app_name = "reservas"
urlpatterns = [
    path("reservaslaboratorios/<int:id_lab>/", reservaslaboratorios , name="reservaslaboratorios"),
    path("reservaslaboratorios/<int:id_lab>/guardar/", guardar_reserva, name="guardar_reserva"),
    path("reservasestaciones/<int:id_lab>/", reservasestaciones , name="reservasestaciones"),
    path("reservasestaciones/<int:id_lab>/estaciones/", estaciones_disponibles, name="estaciones_disponibles"),
    path("reservasestaciones/<int:id_lab>/guardar/", guardar_reserva_estacion, name="guardar_reserva"),

]