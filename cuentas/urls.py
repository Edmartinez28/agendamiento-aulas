
from django.urls import path
from .views import *

app_name = "cuentas"
urlpatterns = [
    path("perfil/", mostrarperfil , name="mostrarperfil"),
]