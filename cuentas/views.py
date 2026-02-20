from django.shortcuts import render
from core.models import *

from django.contrib.auth.decorators import login_required

@login_required
def mostrarperfil(request):
    usuario = request.user
    reservas = Reserva.objects.filter(usuario=usuario)

    contexto = {
        "usuario": usuario,
        "reservas": reservas,
    }

    return render(request, "perfil.html", contexto)


@login_required
def redirect_by_role(request):
    return redirect("/cuentas/perfil/")


@login_required
def perfil(request):
    return render(request, "cuentas/perfil.html")