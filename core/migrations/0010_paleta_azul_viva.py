from django.db import migrations

from core.parametros import PARAMETROS_DEFECTO

# Sólo la paleta. Los textos de marca, los radios, las tipografías y el tema por
# defecto se quedan como los tengas configurados.
#
# OJO: esta migración SÍ pisa los valores que haya en la base, incluido `fondo`.
# Es intencional: es un cambio de paleta, no una siembra de valores que falten.
# Si tienes colores propios que quieras conservar, anótalos antes de aplicarla.
PALETA = [
    "fondo", "marca_fuerte", "senal",
    "estado_aprobada", "estado_revision", "estado_cancelada",
    "estado_finalizada", "estado_bloqueada", "estado_estudiantil",
    "inv_nuevo", "inv_correcto", "inv_pendiente",
    "inv_mantenimiento", "inv_fallando", "inv_baja",
    "claro_sala", "claro_panel", "claro_panel_alto", "claro_ranura", "claro_tinta",
    "oscuro_sala", "oscuro_panel", "oscuro_panel_alto", "oscuro_ranura", "oscuro_tinta",
]

# Paleta anterior (azul pizarra apagado), para poder revertir.
PALETA_ANTERIOR = {
    "fondo": "#4C758A",
    "marca_fuerte": "#3A5C6E",
    "senal": "#12A7BD",
    "estado_aprobada": "#2E7D5B",
    "estado_revision": "#B07514",
    "estado_cancelada": "#C0483D",
    "estado_finalizada": "#3D6E93",
    "estado_bloqueada": "#6B5B95",
    "estado_estudiantil": "#0E8FA3",
    "inv_nuevo": "#0E8FA3",
    "inv_correcto": "#2E7D5B",
    "inv_pendiente": "#B07514",
    "inv_mantenimiento": "#6B5B95",
    "inv_fallando": "#C0483D",
    "inv_baja": "#6B7A84",
    "claro_sala": "#E9EEF2",
    "claro_panel": "#F8FAFC",
    "claro_panel_alto": "#FFFFFF",
    "claro_ranura": "#DFE7ED",
    "claro_tinta": "#16232B",
    "oscuro_sala": "#0E1519",
    "oscuro_panel": "#161F25",
    "oscuro_panel_alto": "#1D272E",
    "oscuro_ranura": "#0A1013",
    "oscuro_tinta": "#E8EFF3",
}


def _aplicar(apps, valores):
    Parametro = apps.get_model("core", "Parametro")

    for etiqueta in PALETA:
        Parametro.objects.update_or_create(
            etiqueta=etiqueta,
            defaults={"valor": valores[etiqueta]},
        )


def paleta_viva(apps, schema_editor):
    _aplicar(apps, PARAMETROS_DEFECTO)


def paleta_apagada(apps, schema_editor):
    _aplicar(apps, PALETA_ANTERIOR)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_alter_laboratorio_estado"),
    ]

    operations = [
        migrations.RunPython(paleta_viva, paleta_apagada),
    ]
