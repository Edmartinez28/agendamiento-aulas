from django.urls import path
from .views import *

app_name = "inventario"
urlpatterns = [
    path("/", inventariototal , name="inventariototal"),
]