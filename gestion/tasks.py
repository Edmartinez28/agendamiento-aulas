import socket
import smtplib
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from itertools import chain
from core.models import Correo  # ajusta import

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_correo_reservas_solicitante(self, solicitante_id: int):
    """
    Envía el correo agrupado por solicitante y marca registros ENVIADO.
    Reintenta si hay fallos de red/timeout/SMTP temporales.
    """
    correos_solicitante = (
        Correo.objects
        .filter(estado="PENDIENTE", solicitante_id=solicitante_id)
        .select_related(
            "solicitante",
            "tecnico",
            "reserva",
            "reserva__laboratorio",
            "reserva__slot",
            "reserva__estacion",
        )
        .order_by("reserva__fecha", "reserva__slot__hora_inicio")
    )

    if not correos_solicitante.exists():
        return {"ok": True, "msg": "Sin pendientes"}

    solicitante = correos_solicitante.first().solicitante
    to_email = getattr(solicitante, "email", None)
    if not to_email:
        # Puedes marcar como CANCELADO o dejar pendiente. Aquí lo marcamos cancelado.
        with transaction.atomic():
            correos_solicitante.update(estado="CANCELADO")
        return {"ok": False, "msg": "Solicitante sin email"}

    # Construir reservas
    reservas_data = []
    for c in correos_solicitante:
        r = c.reserva
        reservas_data.append({
            "fecha": r.fecha,
            "hora_inicio": r.slot.hora_inicio,
            "hora_fin": r.slot.hora_fin,
            "laboratorio": r.laboratorio.nombre,
            "estacion": r.estacion.codigo if r.estacion else "LABORATORIO COMPLETO",
            "estado": r.estado,
            "tipo": r.tipo,
        })

    nombre = (solicitante.get_full_name() or getattr(solicitante, "username", "Usuario")).strip()

    # CC
    emails_tecnicos = correos_solicitante.values_list("tecnico__email", flat=True)
    emails_responsables = correos_solicitante.values_list("reserva__laboratorio__correo_responsable", flat=True)
    cc_list = sorted({
        e.strip().lower()
        for e in chain(emails_tecnicos, emails_responsables)
        if e and str(e).strip()
    })

    # Render template
    context = {
        "nombre": nombre,
        "total": len(reservas_data),
        "reservas": reservas_data,
        "hoy": timezone.localdate().strftime("%d/%m/%Y"),
        "anio": timezone.localdate().year,
        "fondo":"#0049A3",
        "titulos":"#FFFFFF",
    }

    html_content = render_to_string("emails/reservas_detalle.html", context)
    text_content = strip_tags(html_content)

    subject = "Detalle de reservas de laboratorio"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or "no-reply@ucacue.edu.ec"

    # Timeout SMTP
    timeout_seconds = getattr(settings, "EMAIL_TIMEOUT_SECONDS", 15)

    connection = get_connection(
        backend=getattr(settings, "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"),
        timeout=timeout_seconds,
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[to_email],
        cc=cc_list,
        connection=connection,
    )
    email.attach_alternative(html_content, "text/html")

    try:
        email.send(fail_silently=False)
    except (socket.timeout, TimeoutError, OSError, smtplib.SMTPException) as exc:
        # Reintento automático
        raise self.retry(exc=exc)

    # Si envió OK, marca ENVIADO
    with transaction.atomic():
        correos_solicitante.update(estado="ENVIADO")

    return {"ok": True, "to": to_email, "cc": cc_list, "count": len(reservas_data)}
