from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_periodo_2026_2"),
    ]

    operations = [
        migrations.CreateModel(
            name="BloqueoLaboratorio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("motivo", models.CharField(blank=True, max_length=200, null=True)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                (
                    "laboratorio",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bloqueos",
                        to="core.laboratorio",
                    ),
                ),
                (
                    "slot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bloqueos",
                        to="core.timeslot",
                    ),
                ),
            ],
            options={
                "ordering": ["laboratorio__nombre", "slot__hora_inicio"],
                "unique_together": {("laboratorio", "slot")},
            },
        ),
    ]
