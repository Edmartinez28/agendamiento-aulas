from django.shortcuts import render
from django.core.serializers import serialize
from core.models import *
import json

from django.db.models import Count, Q
from django.shortcuts import redirect, get_object_or_404

from datetime import datetime, timedelta
from django.utils import timezone

# Create your views here.
def obtenerlaboratorios(request):
    laboratorios = Laboratorio.objects.all()

    return render(request, "listadolaboratorios.html", {"laboratorios":laboratorios})

def listadoreservas(request, id_lab):
    laboratorio = Laboratorio.objects.get(id=id_lab)

    reservas_laboratorio = Reserva.objects.filter(laboratorio=laboratorio, estacion__isnull=True).order_by('-fecha')
    reservas_estaciones = Reserva.objects.filter(laboratorio=laboratorio, estacion__isnull=False).order_by('-fecha')

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

def obtenerhorario(request, id_lab):
    laboratorio = Laboratorio.objects.get(id=id_lab)
    reservas = Reserva.objects.filter(laboratorio=laboratorio, estacion__isnull=True)
    slots = TimeSlot.objects.all().order_by("hora_inicio")

    contexto = {
        "laboratorio": laboratorio,
        "reservas":reservas,
        "slots":slots
    }
    return render(request, "horariolaboratorio.html", contexto)


def obtenerhorario(request, id_lab):
    laboratorio = get_object_or_404(Laboratorio, id=id_lab)

    # 📅 Obtener fecha base desde GET o usar hoy
    week_str = request.GET.get("week")

    if week_str:
        base_date = datetime.strptime(week_str, "%Y-%m-%d").date()
    else:
        base_date = timezone.localdate()

    # 📅 Calcular lunes de esa semana
    start_week = base_date - timedelta(days=base_date.weekday())
    end_week = start_week + timedelta(days=4)  # Viernes

    # 🔎 Filtrar reservas solo de esa semana
    reservas_qs = Reserva.objects.filter(
        laboratorio=laboratorio,
        estacion__isnull=True,
        fecha__range=(start_week, end_week)
    ).select_related(
        "laboratorio", "slot", "carrera", "ciclo", "paralelo", "usuario"
    )

    slots_qs = TimeSlot.objects.all().order_by("hora_inicio")

    reservas = []
    for r in reservas_qs:
        reservas.append({
            "id": r.id,
            "laboratorio": r.laboratorio.nombre,
            "fecha": r.fecha.strftime("%Y-%m-%d"),
            "hora_inicio": r.slot.hora_inicio.strftime("%H:%M:%S"),
            "hora_fin": r.slot.hora_fin.strftime("%H:%M:%S"),
            "estado": r.estado,
            "asignatura": r.asignatura,
            "carrera": r.carrera.nombre if r.carrera else "",
            "ciclo": r.ciclo.nombre if r.ciclo else "",
            "paralelo": r.paralelo.nombre if r.paralelo else "",
            "grupo": r.grupo,
            "estudiantes": r.estudiantes,
            "tipo": r.tipo,
            "usuario": r.usuario.get_full_name() or r.usuario.username
        })

    slots = []
    for s in slots_qs:
        slots.append({
            "hora_inicio": s.hora_inicio.strftime("%H:%M:%S"),
            "hora_fin": s.hora_fin.strftime("%H:%M:%S"),
        })

    contexto = {
        "laboratorio": laboratorio,
        "reservas": json.dumps(reservas),
        "slots": json.dumps(slots),
        "start_week": start_week.strftime("%Y-%m-%d"),
        "end_week": end_week.strftime("%Y-%m-%d"),
    }

    return render(request, "horariolaboratorio.html", contexto)
