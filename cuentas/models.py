from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ADMIN = "ADMIN"
    DOCENTE = "DOCENTE"
    ESTUDIANTE = "ESTUDIANTE"
    TECNICO = "TECNICO"

    ROLES = [
    (ADMIN, "Administrador"),
    (DOCENTE, "Docente"),
    (ESTUDIANTE, "Estudiante"),
    (TECNICO, "Técnico"),
    ]

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        null=True,
        blank=True
    )

    external_id = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True
    )

    synced_with_erp = models.BooleanField(default=False)

    # 👉 Campo de imagen
    avatar = models.ImageField(
        upload_to="avatars/",   # carpeta dentro de MEDIA_ROOT
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.username} - {self.rol}"