from django.utils import timezone
from datetime import datetime
from .models import Reserva


def marcar_reservas_expiradas():
    now = timezone.now()

    reservas = Reserva.objects.filter(estado="pendiente")

    for r in reservas:
        fecha_hora = datetime.combine(r.fecha, r.hora)

        if fecha_hora < now:
            r.estado = "cancelado"
            r.save()