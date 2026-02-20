
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import *

app_name = "cuentas"
urlpatterns = [
    path("perfil/", mostrarperfil , name="mostrarperfil"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("editar-avatar/", editar_avatar, name="editar_avatar"),
]