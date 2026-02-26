import os
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

class Laboratorio(models.Model):
    ESTADO_CHOICES = [
        ("ACTIVO", "ACTIVO"),
        ("INACTIVO", "INACTIVO"),
        ("EN MANTENIMIENTO", "EN MANTENIMIENTO"),
    ]

    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=150, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="ACTIVO")
    responsable = models.CharField(max_length=100)
    correo_responsable = models.CharField(max_length=100, default="innovacion@ucacue.edu.ec")
    numero_responsable = models.CharField(max_length=100, null=True, blank=True)
    capacidad = models.IntegerField(null=False, default=15)

    imagen = models.ImageField(upload_to='laboratorios/', null=True, blank=True)

    def __str__(self):
        return self.nombre


def laboratorio_upload_path(instance, filename):
    nombre = (instance.laboratorio.nombre or "sin-nombre").strip()
    return os.path.join("laboratorios", nombre, filename)

class ImagenLaboratorio(models.Model):
    laboratorio = models.ForeignKey("Laboratorio", on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to=laboratorio_upload_path, null=True, blank=True)

    def __str__(self):
        return f"{self.laboratorio.nombre} - {self.id}"


class Estacion(models.Model):
    ESTADO_CHOICES = [
        ("ACTIVO", "ACTIVO"),
        ("INACTIVO", "INACTIVO"),
        ("SUSPENDIDO", "SUSPENDIDO"),
    ]

    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE, related_name="estaciones")
    codigo = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50, blank=True, null=True)
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

class Carrera(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre}"

class Ciclo(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre}"

class Paralelo(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre}"

class Reserva(models.Model):

    ESTADOS_CHOICES = [
        ("APROBADA", "APROBADA"),
        ("EN REVISION", "EN REVISION"),
        ("CANCELADA", "CANCELADA"),
        ("FINALIZADA", "FINALIZADA"),
        ("BLOQUEADA", "BLOQUEADA"),
        ("ESTUDIANTIL", "ESTUDIANTIL"),
    ]

    TIPO_CHOICES = [
        ("INDUCCION DOCENTE","INDUCCION DOCENTE"),
        ("INDUCCION ESTUDIANTIL","INDUCCION ESTUDIANTIL"),
        ("CLASES NORMALES","CLASES NORMALES"),
    ]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE, null=True, blank=True) # Encaso de que la estacion este vacia se valida que se reserva el laboratorio completo
    fecha = models.DateField()
    slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default="EN REVISION")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, null=True, blank=True)
    ciclo = models.ForeignKey(Ciclo, on_delete=models.CASCADE, null=True, blank=True)
    paralelo = models.ForeignKey(Paralelo, on_delete=models.CASCADE, null=True, blank=True)
    asignatura = models.CharField(max_length=200, null=True, blank=True)

    grupo = models.IntegerField(null=False, default=1)
    estudiantes = models.IntegerField(null=False, default=1)
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, default="CLASES NORMALES")

    class Meta:
        indexes = [
            models.Index(fields=["laboratorio", "fecha", "slot"]),
            models.Index(fields=["estacion", "fecha", "slot"]),
        ]

    def clean(self):
        reservas_conflicto = Reserva.objects.filter(
            fecha=self.fecha,
            slot=self.slot,
            estado__in=["APROBADA", "EN REVISION"]
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
        #if self.estacion is not None:
        #    self.estado = "ESTUDIANTIL" 
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.laboratorio.nombre} - {self.fecha} - {self.slot.hora_inicio}-{self.slot.hora_fin} - {self.estado}"

class Programa(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.nombre}"

class EstacionPrograma(models.Model):
    estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE, related_name="estacion_programas")
    programa = models.ForeignKey(Programa, on_delete=models.CASCADE, related_name="programa_estaciones")

    def __str__(self):
        return f"{self.estacion.laboratorio.nombre} - {self.estacion.codigo} - {self.programa.nombre}"

class Correo(models.Model):
    ESTADO_CHOICES = [
        ("ENVIADO", "ENVIADO"),
        ("PENDIENTE", "PENDIENTE"),
        ("CANCELADO", "CANCELADO"),
    ]

    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name="correos")
    tecnico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="correos_como_tecnico")
    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="correos_como_solicitante")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="PENDIENTE")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Correo #{self.pk} - Reserva {self.reserva_id} - {self.estado}"

class Parametro(models.Model):
    etiqueta = models.CharField(max_length=100, unique=True)
    valor = models.TextField()

    def __str__(self):
        return f"{self.etiqueta}"