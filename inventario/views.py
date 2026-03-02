from django.shortcuts import render
from core.models import *

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

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

def nuevoinventario(request):
    laboratorios = Laboratorio.objects.all()

    if request.method == "POST":
        laboratorio_id = request.POST.get("laboratorio")
        tipo = (request.POST.get("tipo") or "").strip()
        estado = request.POST.get("estado") or "PENDIENTE"

        # Validaciones mínimas
        if not laboratorio_id:
            messages.error(request, "Debes seleccionar un laboratorio.")
            return render(request, "iteminventario.html", {"laboratorios": laboratorios, "fondo":get_fondo_valor, "titulos":get_letra_titulos})

        if not tipo:
            messages.error(request, "El tipo de equipo es obligatorio.")
            return render(request, "iteminventario.html", {"laboratorios": laboratorios, "fondo":get_fondo_valor, "titulos":get_letra_titulos})

        laboratorio_obj = get_object_or_404(Laboratorio, pk=laboratorio_id)

        inv = Inventario.objects.create(
            laboratorio=laboratorio_obj,
            codigo=request.POST.get("codigo") or "Sin Codigo",
            serie=request.POST.get("serie") or "Sin S/N",
            marca=request.POST.get("marca") or None,
            modelo=request.POST.get("modelo") or None,
            tipo=tipo,
            detalles=request.POST.get("detalles") or None,
            estado=estado,
            observacion=request.POST.get("observacion") or None,
        )

        messages.success(request, f"✅ Equipo creado correctamente: {inv.codigo} ({inv.tipo}).")
        return redirect("inventario:nuevoinventario")  # o a tu listado: redirect("inventario:inventariototal")

    return render(request, "iteminventario.html", {"laboratorios": laboratorios, "fondo":get_fondo_valor, "titulos":get_letra_titulos})

def actualizarinventario(request, item_id):
    laboratorios = Laboratorio.objects.all()
    item = get_object_or_404(Inventario, pk=item_id)

    if request.method == "POST":
        laboratorio_id = request.POST.get("laboratorio")
        tipo = (request.POST.get("tipo") or "").strip()
        estado = request.POST.get("estado") or "PENDIENTE"

        # Validaciones mínimas (como en crear)
        if not laboratorio_id:
            messages.error(request, "Debes seleccionar un laboratorio.")
            return render(request, "iteminventario.html", {"laboratorios": laboratorios, "item": item})

        if not tipo:
            messages.error(request, "El tipo de equipo es obligatorio.")
            return render(request, "iteminventario.html", {"laboratorios": laboratorios, "item": item})

        laboratorio_obj = get_object_or_404(Laboratorio, pk=laboratorio_id)

        # Actualizar campos
        item.laboratorio = laboratorio_obj
        item.codigo = request.POST.get("codigo") or "Sin Codigo"
        item.serie = request.POST.get("serie") or "Sin S/N"
        item.marca = request.POST.get("marca") or None
        item.modelo = request.POST.get("modelo") or None
        item.tipo = tipo
        item.detalles = request.POST.get("detalles") or None
        item.estado = estado
        item.observacion = request.POST.get("observacion") or None

        item.save()

        messages.success(request, f"✅ Equipo actualizado correctamente: {item.codigo} ({item.tipo}).")
        return redirect("inventario:actualizarinventario", item_id=item.id)  # o al listado

    # GET: mostrar form precargado
    return render(request, "iteminventario.html", {"laboratorios": laboratorios, "item": item, "fondo":get_fondo_valor, "titulos":get_letra_titulos})