from django.shortcuts import render
from django.core.serializers import serialize
from core.models import *
import json

from django.db.models import Count, Q
from django.shortcuts import redirect, get_object_or_404

# Create your views here.
def obtenerlaboratorios(request):
    laboratorios = Laboratorio.objects.all()

    return render(request, "listadolaboratorios.html", {"laboratorios":laboratorios})

def listadoreservas(request, id_lab):
    laboratorio = Laboratorio.objects.get(id=id_lab)

    reservas_laboratorio = Reserva.objects.filter(laboratorio=laboratorio, estacion__isnull=True)
    reservas_estaciones = Reserva.objects.filter(laboratorio=laboratorio, estacion__isnull=False)

    total = reservas_laboratorio.count() + reservas_estaciones.count()
    pendientes = Reserva.objects.filter(laboratorio=laboratorio,estado="EN REVISION").count()
    aprobadas = Reserva.objects.filter(laboratorio=laboratorio,estado="ACTIVA").count()
    rechazadas = Reserva.objects.filter(laboratorio=laboratorio,estado="CANCELADA").count()

    contexto = {
        "laboratorio": laboratorio,
        "reservaslaboratorio": reservas_laboratorio,
        "reservasestaciones": reservas_estaciones,
        "total": total,
        "pendientes": pendientes,
        "aprobadas": aprobadas,
        "rechazadas": rechazadas,
    }

    return render(request, "listadoreservas.html", contexto)

def cambiar_estado_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == "POST":
        nuevo_estado = request.POST.get("estado")
        reserva.estado = nuevo_estado
        reserva.save()

    return redirect("gestion:listadoreservas", id_lab=reserva.laboratorio.id)
