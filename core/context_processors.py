import re

from django.db import DatabaseError
from django.utils.safestring import mark_safe

from core.models import Parametro
from core.parametros import PARAMETROS_DEFECTO
from core.periodo import _a_fecha

# Los valores se inyectan literalmente dentro de un bloque <style> en base.html,
# donde el autoescapado de Django no sirve (convertiría las comillas de
# 'Space Grotesk' en entidades y rompería el CSS). En vez de confiar en el
# contenido, se limita a un alfabeto que no puede cerrar la etiqueta ni abrir
# otra: sin < > ; { } @ ni barras.
_CSS_SEGURO = re.compile(r"[^A-Za-z0-9#%().,'\"\-_ /]")

# Etiquetas que no son valores CSS sino texto de interfaz: se dejan intactas
# para la plantilla (que sí las autoescapa) y no se publican como variable CSS.
_SOLO_TEXTO = {
    "marca_nombre", "marca_institucion", "pie_texto",
    "periodo_nombre", "periodo_inicio", "periodo_fin",
}


def _css_seguro(valor):
    return _CSS_SEGURO.sub("", valor)[:120]


def parametros(request):
    """Expone las parametrizaciones de interfaz a todas las plantillas.

    - `parametros`: catálogo completo, tal cual está en la base.
    - `parametros_css`: el subconjunto que `base.html` vuelca como variables
      `--p-<etiqueta>` sobre :root, ya saneado y marcado como seguro.
    - `fondo` / `titulos`: compatibilidad con las vistas que ya los inyectaban.
    """
    valores = dict(PARAMETROS_DEFECTO)
    # Lo que hay en la base tal cual, aunque esté vacío. El periodo lo necesita:
    # para él, campo vacío significa "desactivado", no "usa el valor por defecto".
    crudos = {}

    try:
        for etiqueta, valor in Parametro.objects.values_list("etiqueta", "valor"):
            valor = (valor or "").strip()
            crudos[etiqueta] = valor
            if valor:
                valores[etiqueta] = valor
    except DatabaseError:
        # La base todavía no está migrada (o no responde): seguimos con los
        # valores por defecto en vez de tumbar la página.
        pass

    css = {
        etiqueta: mark_safe(_css_seguro(valor))
        for etiqueta, valor in valores.items()
        if etiqueta not in _SOLO_TEXTO
    }

    # El periodo se deriva de lo que ya leímos: ninguna consulta extra. Se usan
    # los valores crudos para que vaciar el campo lo desactive de verdad.
    def _del_periodo(etiqueta):
        return crudos.get(etiqueta, PARAMETROS_DEFECTO.get(etiqueta, ""))

    inicio = _a_fecha(_del_periodo("periodo_inicio"))
    fin = _a_fecha(_del_periodo("periodo_fin"))

    return {
        "parametros": valores,
        "parametros_css": css,
        "periodo": {
            "nombre": _del_periodo("periodo_nombre") or "Periodo académico",
            "inicio": inicio,
            "fin": fin,
            "activo": bool(inicio or fin),
        },
        "fondo": valores["fondo"],
        "titulos": valores["colortitulos"],
    }
