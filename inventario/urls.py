from django.urls import path
from .views import *

app_name = "inventario"
urlpatterns = [
    path("", inventariototal , name="inventariototal"),
    path("lab/<int:lab_id>/", inventario_por_laboratorio, name="inventario_por_laboratorio"),
]