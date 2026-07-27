from django.db import migrations

from core.parametros import PARAMETROS_DEFECTO


def crear_parametros(apps, schema_editor):
    """Siembra las parametrizaciones de interfaz que aún no existan.

    Es idempotente y no pisa valores ya configurados desde el admin: `fondo` y
    `colortitulos`, si ya están, se quedan como están.
    """
    Parametro = apps.get_model("core", "Parametro")
    existentes = set(Parametro.objects.values_list("etiqueta", flat=True))

    Parametro.objects.bulk_create([
        Parametro(etiqueta=etiqueta, valor=valor)
        for etiqueta, valor in PARAMETROS_DEFECTO.items()
        if etiqueta not in existentes
    ])


def borrar_parametros(apps, schema_editor):
    Parametro = apps.get_model("core", "Parametro")
    # `fondo` y `colortitulos` son anteriores a esta migración: no se tocan.
    etiquetas = [e for e in PARAMETROS_DEFECTO if e not in ("fondo", "colortitulos")]
    Parametro.objects.filter(etiqueta__in=etiquetas).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_reserva_observacion"),
    ]

    operations = [
        migrations.RunPython(crear_parametros, borrar_parametros),
    ]
