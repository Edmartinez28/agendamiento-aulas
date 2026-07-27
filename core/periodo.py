"""Periodo académico vigente.

Las pantallas del usuario final (perfil, listado de reservas, mi horario) sólo
muestran reservas dentro del periodo configurado en `Parametro`. El horario del
aula queda fuera a propósito: ahí se navega semana a semana y el técnico tiene
que poder mirar cualquier fecha.

Criterio ante una configuración incompleta o inválida: NO filtrar ese extremo.
Esconder las reservas de alguien por una errata en el admin es peor que mostrar
de más, y el error es invisible para quien lo sufre.
"""

from datetime import datetime

from django.db import DatabaseError

from core.models import Parametro
from core.parametros import PARAMETROS_DEFECTO

ETIQUETAS = ("periodo_nombre", "periodo_inicio", "periodo_fin")


def _a_fecha(valor):
    try:
        return datetime.strptime((valor or "").strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def periodo_vigente():
    """Devuelve (inicio, fin, nombre). `inicio` y `fin` pueden ser None.

    Aquí el campo vacío NO cae al valor por defecto, al revés que en los colores:
    vaciar `periodo_inicio` o `periodo_fin` desde el admin es la forma de
    desactivar ese extremo del filtro. El respaldo sólo entra si el registro
    todavía no existe (base sin migrar).
    """
    valores = {e: PARAMETROS_DEFECTO.get(e, "") for e in ETIQUETAS}

    try:
        for etiqueta, valor in (
            Parametro.objects.filter(etiqueta__in=ETIQUETAS).values_list("etiqueta", "valor")
        ):
            valores[etiqueta] = (valor or "").strip()
    except DatabaseError:
        pass

    return _a_fecha(valores["periodo_inicio"]), _a_fecha(valores["periodo_fin"]), valores["periodo_nombre"]


def filtrar(queryset, campo="fecha"):
    """Recorta un queryset de reservas al periodo vigente."""
    inicio, fin, _ = periodo_vigente()

    if inicio:
        queryset = queryset.filter(**{campo + "__gte": inicio})
    if fin:
        queryset = queryset.filter(**{campo + "__lte": fin})

    return queryset


def contiene(fecha):
    """¿Esa fecha cae dentro del periodo? Sirve para avisar en `mi horario`
    cuando la semana que se está mirando queda fuera."""
    inicio, fin, _ = periodo_vigente()

    if inicio and fecha < inicio:
        return False
    if fin and fecha > fin:
        return False

    return True
