from datetime import date, datetime

from .forms import generar_slots
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, FormView

from config import settings
from reservas.forms import RegisterForm, ReservaForm, ContactoForm
from reservas.models import Reserva


class HomeView(TemplateView):
    template_name = "reservas/home.html"

class ServiciosView(TemplateView):
    template_name = "reservas/servicios.html"

class ContactosView(FormView):
    template_name = "reservas/contactos.html"

    form_class = ContactoForm

    success_url = reverse_lazy('contactos')

    def form_valid(self, form):
        nombre = form.cleaned_data['nombre']
        email = form.cleaned_data['email']
        asunto = form.cleaned_data['asunto']
        mensaje = form.cleaned_data['mensaje']

        mensaje_completo = f"""
        Nombre: {nombre}
        Email: {email}
        
        Mensaje: {mensaje}
        """

        email = EmailMessage(
            subject=asunto,
            body=mensaje_completo,
            from_email=settings.EMAIL_HOST_USER,
            to=["danixdxdfortnite@gmail.com"],
            reply_to=[email],  # 👈 clave
        )

        email.send(fail_silently=False)

        messages.success(self.request, "Mensaje enviado correctamente")
        
        return super().form_valid(form)


class SomosView(TemplateView):
    template_name = "reservas/somos.html"

def horas_disponibles_api(request):
    fecha_str = request.GET.get('fecha')
    if not fecha_str:
        return JsonResponse({'horas': []})
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'horas': []})
    slots = generar_slots(fecha)   # lista de objetos time
    horas = [s.strftime('%H:%M') for s in slots]
    return JsonResponse({'horas': horas})

class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservas/crear_reserva.html'
    success_url = reverse_lazy('reservas:home')  # o donde quieras

    def get_initial(self):
        # Devuelve un diccionario con la fecha actual como valor inicial
        return {'fecha': date.today()}

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrige los errores del formulario.')
        return super().form_invalid(form)


