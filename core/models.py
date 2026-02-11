from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone


class Laboratorio(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=150, blank=True, null=True)
    estado = models.CharField(max_length=20, default="ACTIVO")
    responsable = models.CharField(max_length=100)
    capacidad = models.IntegerField(null=False, default=15)

    def __str__(self):
        return self.nombre


class Estacion(models.Model):
    ESTADO_CHOICES = [
        ("ACTIVO", "ACTIVO"),
        ("INACTIVO", "INACTIVO"),
        ("SUSPENDIDO", "SUSPENDIDO"),
    ]

    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE, related_name="estaciones")
    codigo = models.CharField(max_length=50)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="ACTIVO")

    def __str__(self):
        return f"{self.laboratorio.nombre} - {self.codigo}"


class TimeSlot(models.Model):
    TIPO_CHOICES = [
        ("HABIL", "HABIL"),
        ("BLOQUEADA", "BLOQUEADA"),
    ]
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="HABIL")

    class Meta:
        unique_together = ("hora_inicio", "hora_fin")
        ordering = ["hora_inicio"]

    def __str__(self):
        return f"{self.hora_inicio} - {self.hora_fin}"

class Reserva(models.Model):

    ESTADOS_CHOICES = [
        ("ACTIVA", "ACTIVA"),
        ("CANCELADA", "CANCELADA"),
        ("FINALIZADA", "FINALIZADA"),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE, null=True, blank=True) # Encaso de que la estacion este vacia se valida que se reserva el laboratorio completo
    fecha = models.DateField()
    slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default="ACTIVA")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["laboratorio", "fecha", "slot"]),
            models.Index(fields=["estacion", "fecha", "slot"]),
        ]

    def clean(self):
        reservas_conflicto = Reserva.objects.filter(
            fecha=self.fecha,
            slot=self.slot,
            estado="ACTIVA"
        ).exclude(pk=self.pk)

        # CASO 1 — reserva del laboratorio completo
        if self.estacion is None:

            conflicto = reservas_conflicto.filter(
                laboratorio=self.laboratorio
            ).exists()

            if conflicto:
                raise ValidationError(
                    "El laboratorio o alguna de sus estaciones ya está reservado en este horario."
                )

        # CASO 2 — reserva de estación
        else:

            conflicto = reservas_conflicto.filter(
                Q(laboratorio=self.laboratorio, estacion__isnull=True)
                |
                Q(estacion=self.estacion)
            ).exists()

            if conflicto:
                raise ValidationError(
                    "La estación o el laboratorio ya está reservado en este horario."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Programa(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.nombre}"

class EstacionPrograma(models.Model):
    estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE, related_name="estaciones")
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE, related_name="programas")

    def __str__(self):
        return f"{self.estacion.laboratorio.nombre} - {self.estacion.nombre} - {self.programa.nombre}"