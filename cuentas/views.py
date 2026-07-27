import json
from datetime import datetime, timedelta

from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import AvatarForm
from core import periodo
from core.models import *
from django.contrib.auth.decorators import login_required
from .models import User

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

    # Sólo el periodo académico vigente: al docente le sirve lo que tiene ahora,
    # no lo que reservó hace tres semestres.
    reservas = (
        periodo.filtrar(Reserva.objects.filter(usuario=usuario))
        .select_related("laboratorio", "slot", "estacion", "carrera", "ciclo", "paralelo")
        .order_by("-fecha", "-slot__hora_inicio")
    )

    contexto = {
        "usuario": usuario,
        "reservas": reservas,
        "fondo":get_fondo_valor,
        "titulos":get_letra_titulos,
    }

    return render(request, "perfil.html", contexto)

@login_required
def mihorario(request):
    """Horario semanal del usuario: sólo sus propias reservas.

    Mismo formato de rejilla que el horario del aula, pero recorriendo TODAS las
    aulas: un docente puede tener bloques en varias, y un estudiante ve aquí sus
    estaciones. Por eso cada bloque lleva el nombre del aula, que en el horario
    del aula sobraba.
    """
    week_str = request.GET.get("week")

    # Un ?week= corrupto no debe tumbar la página: se cae a la semana actual.
    base_date = timezone.localdate()
    if week_str:
        try:
            base_date = datetime.strptime(week_str, "%Y-%m-%d").date()
        except ValueError:
            pass

    start_week = base_date - timedelta(days=base_date.weekday())  # lunes
    end_week = start_week + timedelta(days=4)                     # viernes

    reservas_qs = (
        periodo.filtrar(
            Reserva.objects.filter(usuario=request.user, fecha__range=(start_week, end_week))
        )
        .select_related("laboratorio", "slot", "estacion", "carrera", "ciclo", "paralelo")
        .order_by("fecha", "slot__hora_inicio")
    )

    reservas = []
    minutos_totales = 0

    for r in reservas_qs:
        reservas.append({
            "id": r.id,
            "laboratorio": r.laboratorio.nombre,
            "ubicacion": r.laboratorio.ubicacion or "",
            "estacion": r.estacion.codigo if r.estacion else "",
            "fecha": r.fecha.strftime("%Y-%m-%d"),
            "hora_inicio": r.slot.hora_inicio.strftime("%H:%M:%S"),
            "hora_fin": r.slot.hora_fin.strftime("%H:%M:%S"),
            "estado": r.estado,
            "tipo": r.tipo,
            "asignatura": r.asignatura or "",
            "carrera": r.carrera.nombre if r.carrera else "",
            "ciclo": r.ciclo.nombre if r.ciclo else "",
            "paralelo": r.paralelo.nombre if r.paralelo else "",
            "grupo": r.grupo,
            "estudiantes": r.estudiantes,
            "observacion": r.observacion or "",
            "responsable": r.laboratorio.responsable,
            "correo_responsable": r.laboratorio.correo_responsable,
        })

        # Sólo cuentan las horas que de verdad vas a ocupar el aula.
        if r.estado in ("APROBADA", "ESTUDIANTIL", "FINALIZADA"):
            inicio = r.slot.hora_inicio.hour * 60 + r.slot.hora_inicio.minute
            fin = r.slot.hora_fin.hour * 60 + r.slot.hora_fin.minute
            minutos_totales += max(0, fin - inicio)

    slots = [
        {
            "hora_inicio": s.hora_inicio.strftime("%H:%M:%S"),
            "hora_fin": s.hora_fin.strftime("%H:%M:%S"),
        }
        for s in TimeSlot.objects.all().order_by("hora_inicio")
    ]

    contexto = {
        "reservas": json.dumps(reservas),
        "slots": json.dumps(slots),
        "start_week": start_week.strftime("%Y-%m-%d"),
        "end_week": end_week.strftime("%Y-%m-%d"),
        "total_semana": len(reservas),
        "horas_semana": round(minutos_totales / 60, 1),
        "aulas_semana": len({r["laboratorio"] for r in reservas}),
        "pendientes_semana": sum(1 for r in reservas if r["estado"] == "EN REVISION"),
        # Si la semana entera cae fuera del periodo, el vacío no es "no tienes
        # reservas": es "aquí no hay nada que mirar". Conviene distinguirlo.
        "fuera_de_periodo": not (periodo.contiene(start_week) or periodo.contiene(end_week)),
    }

    return render(request, "mihorario.html", contexto)


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

