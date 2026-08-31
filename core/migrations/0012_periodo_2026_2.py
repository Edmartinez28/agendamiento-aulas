"""Traslada el periodo académico vigente al 2026-2.

`core/parametros.py` sólo es el respaldo para una base sin sembrar: en cuanto
los registros existen (los creó `0011_periodo_academico`), lo que manda es la
base. Cambiar el diccionario no basta, hace falta mover las filas.

Los valores van aquí escritos a mano, no importados de `PARAMETROS_DEFECTO`:
una migración tiene que hacer siempre lo mismo, y el diccionario volverá a
cambiar cuando empiece el 2027-1.

Sólo se toca la fila que todavía tiene el valor del 2026-1. Si alguien ya la
ajustó desde el admin, su fecha gana: pisarla dejaría a los usuarios sin ver
sus reservas sin que nadie tocase el admin.
"""

from django.db import migrations

ANTERIOR = {
    "periodo_nombre": "Periodo académico 2026-1",
    "periodo_inicio": "2026-02-01",
    "periodo_fin": "2026-08-31",
}

NUEVO = {
    "periodo_nombre": "Periodo académico 2026-2",
    "periodo_inicio": "2026-09-01",
    "periodo_fin": "2027-01-31",
}


def _mover(apps, desde, hasta):
    Parametro = apps.get_model("core", "Parametro")

    for etiqueta, valor_viejo in desde.items():
        Parametro.objects.filter(etiqueta=etiqueta, valor=valor_viejo).update(
            valor=hasta[etiqueta]
        )


def avanzar(apps, schema_editor):
    _mover(apps, ANTERIOR, NUEVO)


def retroceder(apps, schema_editor):
    _mover(apps, NUEVO, ANTERIOR)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_periodo_academico"),
    ]

    operations = [
        migrations.RunPython(avanzar, retroceder),
    ]
