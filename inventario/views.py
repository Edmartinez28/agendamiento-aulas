from django.shortcuts import render
from core.models import *

from django.shortcuts import render, get_object_or_404


# Inicio de parametrizaciones de color base
def get_fondo_valor(default="#4C758A"):
    p = Parametro.objects.filter(etiqueta="fondo").first()
    return p.valor if p else default

def get_letra_titulos(default="#FFFFFF"):
    p = Parametro.objects.filter(etiqueta="colortitulos").first()
    return p.valor if p else default


def inventariototal(request):
    qs = Inventario.objects.select_related("laboratorio").all().order_by("-fecha_ingreso")

    inventario_data = []
    for i in qs:
        inventario_data.append({
            "id": i.id,
            "laboratorio": {"nombre": i.laboratorio.nombre if i.laboratorio else ""},
            "codigo": i.codigo,
            "serie": i.serie,
            "marca": i.marca,
            "modelo": i.modelo,
            "tipo": i.tipo,
            "detalles": i.detalles,
            "estado": i.estado,
            "observacion": i.observacion,
            "fecha_ingreso": i.fecha_ingreso.isoformat(),  # importante para JS
        })

    contexto = {"inventario_json": inventario_data, "fondo":get_fondo_valor, "titulos":get_letra_titulos,}
    return render(request, "inventario.html", contexto)

def inventario_por_laboratorio(request, lab_id):
    laboratorio = get_object_or_404(Laboratorio, pk=lab_id)

    qs = (
        Inventario.objects.select_related("laboratorio")
        .filter(laboratorio_id=laboratorio.id)
        .order_by("-fecha_ingreso")
    )

    inventario_data = []
    for i in qs:
        inventario_data.append({
            "id": i.id,
            "laboratorio": {"nombre": i.laboratorio.nombre if i.laboratorio else ""},
            "codigo": i.codigo,
            "serie": i.serie,
            "marca": i.marca,
            "modelo": i.modelo,
            "tipo": i.tipo,
            "detalles": i.detalles,
            "estado": i.estado,
            "observacion": i.observacion,
            "fecha_ingreso": i.fecha_ingreso.isoformat(),
        })

    contexto = {
        "inventario_json": inventario_data,
        "laboratorio": laboratorio,
        "fondo":get_fondo_valor,
        "titulos":get_letra_titulos,
    }
    return render(request, "inventario.html", contexto)