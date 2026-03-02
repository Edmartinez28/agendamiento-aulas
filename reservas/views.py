from django.shortcuts import render
from django.core.serializers import serialize
from core.models import *
import json

from datetime import date, timedelta
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.db import transaction

# Inicio de parametrizaciones de color base
def get_fondo_valor(default="#4C758A"):
    p = Parametro.objects.filter(etiqueta="fondo").first()
    return p.valor if p else default

def get_letra_titulos(default="#FFFFFF"):
    p = Parametro.objects.filter(etiqueta="colortitulos").first()
    return p.valor if p else default

def reservaslaboratorios(request, id_lab):
    carreras = Carrera.objects.all()
    ciclos = Ciclo.objects.all()
    paralelos = Paralelo.objects.all()

    laboratorio = Laboratorio.objects.get(id=id_lab)
    slots = list(TimeSlot.objects.all().order_by("hora_inicio").values("id", "hora_inicio", "hora_fin", "tipo"))
    for s in slots:
        s["hora_inicio"] = s["hora_inicio"].strftime("%H:%M")
        s["hora_fin"] = s["hora_fin"].strftime("%H:%M")
        s["label"] = f"{s['hora_inicio']} - {s['hora_fin']}"
    
    # Obtenemos la semana y las reservas ------------------------------
    week_offset = int(request.GET.get("week", 0))
    today = timezone.localdate()

    # Obtener lunes de la semana actual
    start_of_week = today - timedelta(days=today.weekday())
    start_of_week += timedelta(weeks=week_offset)

    end_of_week = start_of_week + timedelta(days=4)  # lunes a viernes

    reservas = Reserva.objects.filter(
        laboratorio=laboratorio,
        fecha__range=[start_of_week, end_of_week],
        estado__in=["APROBADA", "EN REVISION", "ESTUDIANTIL"]
    ).select_related("slot")

    reservas_data = [
        {
            "fecha": r.fecha.strftime("%Y-%m-%d"),
            "slot_id": r.slot.id,
            "estado":r.estado,
        }
        for r in reservas
    ]

    # Si es petición AJAX → solo devolver JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "start_of_week": start_of_week.strftime("%Y-%m-%d"),
            "end_of_week": end_of_week.strftime("%Y-%m-%d"),
            "reservas": reservas_data,
        })

    imagenes = ImagenLaboratorio.objects.filter(laboratorio=laboratorio)

    contexto = {
        "laboratorio":laboratorio,
        "carreras":carreras,
        "ciclos":ciclos,
        "paralelos":paralelos,
        "slots": slots,
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
        "reservas_json": reservas_data,
        "fondo":get_fondo_valor,
        "imagenes":imagenes,
        "titulos":get_letra_titulos,
    }
    return render(request, "reservaslaboratorios.html", contexto)


#@require_POST
#@login_required
def guardar_reserva(request, id_lab):
    try:
        data = json.loads(request.body)

        laboratorio = Laboratorio.objects.get(id=id_lab)

        asignatura = data.get("asignatura")
        carrera_id = data.get("carrera")
        ciclo_id = data.get("ciclo")
        paralelo_id = data.get("paralelo")
        grupo = data.get("grupo")
        estudiantes = data.get("numEstudiantes")
        horarios = data.get("horarios")

        if not horarios:
            return JsonResponse({"error": "No hay horarios seleccionados"}, status=400)

        with transaction.atomic():

            for item in horarios:
                fecha_str, slot_id = item.rsplit("-", 1)
                fecha = parse_date(fecha_str)

                reserva = Reserva(
                    usuario=request.user,
                    laboratorio=laboratorio,
                    fecha=fecha,
                    slot_id=slot_id,
                    asignatura=asignatura,
                    carrera_id=carrera_id,
                    ciclo_id=ciclo_id,
                    paralelo_id=paralelo_id,
                    grupo=grupo,
                    estudiantes=estudiantes,
                )

                reserva.full_clean()  # 🔥 valida conflictos
                reserva.save()

        return JsonResponse({"success": True})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def reservasestaciones(request, id_lab):

    carreras = Carrera.objects.all()
    ciclos = Ciclo.objects.all()
    paralelos = Paralelo.objects.all()

    laboratorio = Laboratorio.objects.get(id=id_lab)
    slots = list(TimeSlot.objects.all().order_by("hora_inicio").values("id", "hora_inicio", "hora_fin", "tipo"))
    for s in slots:
        s["hora_inicio"] = s["hora_inicio"].strftime("%H:%M")
        s["hora_fin"] = s["hora_fin"].strftime("%H:%M")
        s["label"] = f"{s['hora_inicio']} - {s['hora_fin']}"
    
    # Obtenemos la semana y las reservas ------------------------------
    week_offset = int(request.GET.get("week", 0))
    today = timezone.localdate()

    # Obtener lunes de la semana actual
    start_of_week = today - timedelta(days=today.weekday())
    start_of_week += timedelta(weeks=week_offset)

    end_of_week = start_of_week + timedelta(days=4)  # lunes a viernes

    habilitadas = Reserva.objects.filter(
        laboratorio=laboratorio,
        fecha__range=[start_of_week, end_of_week],
        estado__in=["ESTUDIANTIL"]
    ).select_related("slot")

    habilitadas_data = [
        {
            "fecha": r.fecha.strftime("%Y-%m-%d"),
            "slot_id": r.slot.id,
            "estado":r.estado,
        }
        for r in habilitadas
    ]

    # Si es petición AJAX → solo devolver JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "start_of_week": start_of_week.strftime("%Y-%m-%d"),
            "end_of_week": end_of_week.strftime("%Y-%m-%d"),
            "habilitadas": habilitadas_data,
        })

    imagenes = ImagenLaboratorio.objects.filter(laboratorio=laboratorio)

    contexto = {
        "laboratorio":laboratorio,
        "carreras":carreras,
        "ciclos":ciclos,
        "paralelos":paralelos,
        "slots": slots,
        "start_of_week": start_of_week,
        "end_of_week": end_of_week,
        "habilitadas_json": habilitadas_data,
        "fondo":get_fondo_valor,
        "imagenes":imagenes,
        "titulos":get_letra_titulos,
    }

    return render(request, "reservasestaciones.html", contexto)


def estaciones_disponibles(request, id_lab):
    fecha = request.GET.get("fecha")
    slot_id = request.GET.get("slot_id")

    laboratorio = Laboratorio.objects.get(id=id_lab)

    estaciones = Estacion.objects.filter(laboratorio=laboratorio, estado="ACTIVO")

    # Reservas existentes en ese slot
    reservas = Reserva.objects.filter(
        laboratorio=laboratorio,
        fecha=fecha,
        slot_id=slot_id,
        estado__in=["APROBADA", "EN REVISION"]
    )

    estaciones_ocupadas = reservas.values_list("estacion_id", flat=True)

    data = []
    for e in estaciones:
        data.append({
            "id": e.id,
            "codigo": e.codigo,
            "modelo": e.modelo,
            "estado": e.estado,
            "ocupada": e.id in estaciones_ocupadas
        })

    return JsonResponse({"estaciones": data})


def guardar_reserva_estacion(request, id_lab):

    laboratorio = Laboratorio.objects.get(id=id_lab)

    if request.method == "POST":
        data = json.loads(request.body)

        asignatura = data.get("asignatura")
        carrera_id = data.get("carrera")
        ciclo_id = data.get("ciclo")
        paralelo_id = data.get("paralelo")
        estacion_id = data.get("estacion_id")
        slot_id = data.get("slot_id")
        fecha = data.get("fecha")

        # ejemplo guardado
        Reserva.objects.create(
            laboratorio = laboratorio,
            asignatura=asignatura,
            carrera_id=carrera_id,
            ciclo_id=ciclo_id,
            paralelo_id=paralelo_id,
            estacion_id=estacion_id,
            slot_id=slot_id,
            fecha=fecha,
            usuario=request.user
        )

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Método no permitido"})