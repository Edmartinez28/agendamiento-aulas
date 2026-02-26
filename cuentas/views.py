from django.shortcuts import render, redirect
from .forms import AvatarForm
from core.models import *

from django.contrib.auth.decorators import login_required


# Inicio de parametrizaciones de color base
def get_fondo_valor(default="#4C758A"):
    p = Parametro.objects.filter(etiqueta="fondo").first()
    return p.valor if p else default

def get_letra_titulos(default="#FFFFFF"):
    p = Parametro.objects.filter(etiqueta="colortitulos").first()
    return p.valor if p else default

def home(request):
    return render(request, "home.html")
    
@login_required
def mostrarperfil(request):
    usuario = request.user
    reservas = Reserva.objects.filter(usuario=usuario)

    contexto = {
        "usuario": usuario,
        "reservas": reservas,
        "fondo":get_fondo_valor,
        "titulos":get_letra_titulos,
    }

    return render(request, "perfil.html", contexto)


@login_required
def redirect_by_role(request):
    return redirect("/cuentas/perfil/")


@login_required
def perfil(request):
    return render(request, "cuentas/perfil.html")

# views.py

@login_required
def editar_avatar(request):
    if request.method == "POST":
        form = AvatarForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("cuentas:mostrarperfil")  # tu url del perfil
    else:
        form = AvatarForm(instance=request.user)

    return render(request, "editar_avatar.html", {"form": form})