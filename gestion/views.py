from django.shortcuts import render, redirect, get_object_or_404
from django.core.serializers import serialize
from core.models import *
import json

from django.db.models import Count, Q

from datetime import datetime, timedelta
from django.utils import timezone

import socket
import smtplib
from collections import defaultdict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from itertools import chain

from django.contrib import messages
from .tasks import enviar_correo_reservas_solicitante

# Inicio de parametrizaciones de color base
def get_fondo_valor(default="#4C758A"):
    p = Parametro.objects.filter(etiqueta="fondo").first()
    return p.valor if p else default

def get_letra_titulos(default="#FFFFFF"):
    p = Parametro.objects.filter(etiqueta="colortitulos").first()
    return p.valor if p else default

# Create your views here.
def obtenerlaboratorios(request):
    laboratorios = Laboratorio.objects.all().prefetch_related(
        "estaciones__estacion_programas__programa"
    )

    for lab in laboratorios:
        programas = Programa.objects.filter(
            programa_estaciones__estacion__laboratorio=lab
        ).distinct()
        lab.programas_unicos = programas

    return render(request, "listadolaboratorios.html", {"laboratorios": laboratorios, "fondo":get_fondo_valor, "titulos":get_letra_titulos})

def listadoreservas(request, id_lab):
    laboratorio = Laboratorio.objects.get(id=id_lab)

    reservas_laboratorio = Reserva.objects.filter(laboratorio=laboratorio, estacion__isnull=True).order_by('-fecha')
    reservas_estaciones = Reserva.objects.filter(laboratorio=laboratorio, estacion__isnull=False).order_by('-fecha')

    total = reservas_laboratorio.count() + reservas_estaciones.count()
    pendientes = Reserva.objects.filter(laboratorio=laboratorio,estado="EN REVISION").count()
    aprobadas = Reserva.objects.filter(laboratorio=laboratorio,estado="APROBADA").count()
    rechazadas = Reserva.objects.filter(laboratorio=laboratorio,estado="CANCELADA").count()

    contexto = {
        "laboratorio": laboratorio,
        "reservaslaboratorio": reservas_laboratorio,
        "reservasestaciones": reservas_estaciones,
        "total": total,
        "pendientes": pendientes,
        "aprobadas": aprobadas,
        "rechazadas": rechazadas,
        "fondo":get_fondo_valor,
        "titulos":get_letra_titulos,
    }

    return render(request, "listadoreservas.html", contexto)

def cambiar_estado_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == "POST":
        nuevo_estado = request.POST.get("estado")
        estado_anterior = reserva.estado

        ESTADOS_VALIDOS = {"APROBADA", "EN REVISION", "CANCELADA"}

        if nuevo_estado and nuevo_estado != estado_anterior and nuevo_estado in ESTADOS_VALIDOS: # Solo si cambia el estado, actualiza y crea correo
            reserva.estado = nuevo_estado
            reserva.save()

            Correo.objects.create(
                reserva=reserva,
                tecnico=request.user,
                solicitante=reserva.usuario,
                estado="PENDIENTE"
            )

    return redirect("gestion:listadoreservas", id_lab=reserva.laboratorio.id)

def obtenerhorario(request, id_lab):
    laboratorio = get_object_or_404(Laboratorio, id=id_lab)
    week_str = request.GET.get("week") # Obtener fecha base desde GET o usar hoy

    if week_str:
        base_date = datetime.strptime(week_str, "%Y-%m-%d").date()
    else:
        base_date = timezone.localdate()

    start_week = base_date - timedelta(days=base_date.weekday()) # Calcular lunes de esa semana
    end_week = start_week + timedelta(days=4)  # Viernes

    reservas_qs = Reserva.objects.filter( # Filtrar reservas solo de esa semana
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
        "fondo":get_fondo_valor,
        "titulos":get_letra_titulos,
    }

    return render(request, "horariolaboratorio.html", contexto)


@login_required
def correos_pendientes_agrupados(request):
    # Traemos correos pendientes con sus reservas (optimizado)
    correos_qs = (
        Correo.objects
        .filter(estado="PENDIENTE")
        .select_related(
            "solicitante",
            "tecnico",
            "reserva",
            "reserva__laboratorio",
            "reserva__slot",
            "reserva__estacion",
            "reserva__carrera",
            "reserva__ciclo",
            "reserva__paralelo",
        )
        .order_by("solicitante__id", "reserva__fecha", "reserva__slot__hora_inicio")
    )

    # Agrupar en Python por solicitante (fácil de renderizar)
    grupos = defaultdict(list)
    for c in correos_qs:
        grupos[c.solicitante].append(c)

    # Acción: enviar o cancelar (por solicitante)
    if request.method == "POST":
        action = request.POST.get("action")  # "enviar" | "cancelar"
        solicitante_id = request.POST.get("solicitante_id")

        if not action or not solicitante_id:
            messages.error(request, "Solicitud inválida.")
            return redirect("gestion:correos_pendientes_agrupados")

        # Re-consulta segura en BD para ese solicitante (evitar manipulación)
        correos_solicitante = (
            Correo.objects
            .filter(estado="PENDIENTE", solicitante_id=solicitante_id)
            .select_related(
                "solicitante",
                "tecnico",
                "reserva",
                "reserva__laboratorio",
                "reserva__slot",
                "reserva__estacion",
                "reserva__carrera",
                "reserva__ciclo",
                "reserva__paralelo",
            )
            .order_by("reserva__fecha", "reserva__slot__hora_inicio")
        )

        if not correos_solicitante.exists():
            messages.warning(request, "No hay correos pendientes para ese solicitante.")
            return redirect("gestion:correos_pendientes_agrupados")

        solicitante = correos_solicitante.first().solicitante

        if action == "cancelar":
            with transaction.atomic():
                correos_solicitante.update(estado="CANCELADO")
            messages.success(request, f"Registros de correo cancelados para {solicitante}.")
            return redirect("gestion:correos_pendientes_agrupados")

        if action == "enviar":
            # Validaciones mínimas:
            solicitante = correos_solicitante.first().solicitante
            if not getattr(solicitante, "email", None):
                messages.error(request, "El solicitante no tiene correo registrado.")
                return redirect("gestion:correos_pendientes_agrupados")

            # Encolar tarea
            enviar_correo_reservas_solicitante.delay(int(solicitante_id))

            messages.success(request, f"Correo en cola para {solicitante}. Se enviará en segundo plano.")
            return redirect("gestion:correos_pendientes_agrupados")

        messages.error(request, "Acción no reconocida.")
        return redirect("gestion:correos_pendientes_agrupados")

    # GET: render pantalla
    context = {
        "grupos": dict(grupos),  # {User: [Correo, Correo, ...]}
        "fondo":get_fondo_valor,
        "titulos":get_letra_titulos,
    }
    return render(request, "correos_pendientes_agrupados.html", context)


def testcorreo(request):
    return render(request, "emails/reservas_detalle.html")
