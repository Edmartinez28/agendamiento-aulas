from django.urls import path
from .views import *

app_name = "gestion"
urlpatterns = [
    path("laboratorios/", obtenerlaboratorios , name="obtenerlaboratorios"),
    path("reservas/<int:id_lab>/", listadoreservas , name="listadoreservas"),
    path("reservas/<int:reserva_id>/estado/",cambiar_estado_reserva,name="cambiar_estado_reserva"),
]