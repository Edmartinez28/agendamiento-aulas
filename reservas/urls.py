from django.urls import path
from .views import *

app_name = "reservas"
urlpatterns = [
    path("reservaslaboratorios/<int:id_lab>/", reservaslaboratorios , name="reservaslaboratorios"),
    path("reservaslaboratorios/<int:id_lab>/guardar/", guardar_reserva, name="guardar_reserva"),
]