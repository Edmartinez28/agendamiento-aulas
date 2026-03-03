from django.shortcuts import render
from core.models import Parametro

def get_fondo_valor(default="#4C758A"):
    p = Parametro.objects.filter(etiqueta="fondo").first()
    return p.valor if p else default

def get_letra_titulos(default="#FFFFFF"):
    p = Parametro.objects.filter(etiqueta="colortitulos").first()
    return p.valor if p else default


def error_404(request, exception):
    contexto = {"fondo":get_fondo_valor, "titulos":get_letra_titulos}
    return render(request, "404.html", contexto, status=404)

def error_500(request):
    contexto = {"fondo":get_fondo_valor, "titulos":get_letra_titulos}
    return render(request, "500.html", contexto, status=500)