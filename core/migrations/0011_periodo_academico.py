from django.db import migrations

from core.parametros import PARAMETROS_DEFECTO

ETIQUETAS = ("periodo_nombre", "periodo_inicio", "periodo_fin")


def crear(apps, schema_editor):
    """Siembra el periodo académico si aún no existe.

    Siembra el periodo que en ese momento tenga `core/parametros.py`; sobre una
    base ya sembrada, quien mueve las fechas al siguiente semestre es una
    migración de datos posterior (ver `0012_periodo_2026_2`) o el admin.
    """
    Parametro = apps.get_model("core", "Parametro")
    existentes = set(Parametro.objects.values_list("etiqueta", flat=True))

    Parametro.objects.bulk_create([
        Parametro(etiqueta=etiqueta, valor=PARAMETROS_DEFECTO[etiqueta])
        for etiqueta in ETIQUETAS
        if etiqueta not in existentes
    ])


def borrar(apps, schema_editor):
    Parametro = apps.get_model("core", "Parametro")
    Parametro.objects.filter(etiqueta__in=ETIQUETAS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_paleta_azul_viva"),
    ]

    operations = [
        migrations.RunPython(crear, borrar),
    ]
