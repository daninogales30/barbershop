import os

import resend
from django.utils import timezone
from datetime import datetime
from .models import Reserva


def marcar_reservas_completadas():

    now = timezone.now()

    reservas = Reserva.objects.filter(estado="pendiente")

    for r in reservas:

        fecha_hora = datetime.combine(r.fecha, r.hora)

        fecha_hora = timezone.make_aware(fecha_hora)

        if fecha_hora < now:

            r.estado = "completado"
            r.save()

resend.api_key = os.getenv("RESEND_API_KEY")


def enviar_email_contacto(asunto, nombre, email_usuario, mensaje):
    try:
        resend.Emails.send({
            "from": "Barbería <onboarding@resend.dev>",
            "to": ["danixdxdfortnite@gmail.com"],
            "subject": asunto,
            "html": f"""
                <h3>Nuevo mensaje de contacto</h3>
                <p><b>Nombre:</b> {nombre}</p>
                <p><b>Email:</b> {email_usuario}</p>
                <p><b>Mensaje:</b><br>{mensaje}</p>
            """
        })
        return True

    except Exception as e:
        print("Error Resend:", e)
        return False


def send_verification_email(to_email, link):
    resend.Emails.send({
        "from": "BarberShop <onboarding@resend.dev>",
        "to": to_email,
        "subject": "Activa tu cuenta",
        "html": f"""
            <h2>Bienvenido a BarberShop</h2>
            <p>Haz click para activar tu cuenta:</p>
            <a href="{link}">Activar cuenta</a>
        """
    })


