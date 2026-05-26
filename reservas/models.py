from django.db import models
from django.db.models import Q

from config import settings

class Reserva(models.Model):
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
        ('completado', 'Completado'),
    ]

    TIPO_CORTE_CHOICES = [
        ('corte_tijera', 'Corte a tijera'),
        ('corte_maquina', 'Corte a máquina'),
        ('solo_barba', 'Solo barba'),
        ('corte_barba', 'Corte + barba'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    tipo_corte = models.CharField(max_length=20, choices=TIPO_CORTE_CHOICES, default='corte_maquina')
    estado = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pendiente')
    notas = models.TextField(blank=True, null=True, help_text="Indicaciones especiales (opcional)")
    telefono = models.CharField(max_length=15, blank=False, help_text="Teléfono de contacto (obligatorio)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['fecha', 'hora'],
                condition=Q(estado__in=['pendiente', 'confirmado']),
                name='unique_active_slot'
            )
        ]
        ordering = ['-fecha', '-hora']

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha} {self.hora} - {self.get_tipo_corte_display()}"

    def total_citas_usuario(self):
        return Reserva.objects.filter(usuario=self.usuario).count()

    def citas_pendientes_usuario(self):
        return Reserva.objects.filter(usuario=self.usuario, estado='pendiente').count()


class Contactoform(models.Model):
    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    asunto = models.CharField(max_length=150)
    mensaje = models.TextField()