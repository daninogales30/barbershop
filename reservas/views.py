from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.core.mail import send_mail, EmailMessage
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

""" class ReservasCreateView(LoginRequiredMixin, CreateView): """

class RegisterView(LoginRequiredMixin, FormView):
    template_name = "registration/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password)

        login(self.request, user)
        
        return super().form_valid(form)

class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    success_url = reverse_lazy('home')
    template_name = "reservas/crear_reserva.html"

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    def get_next_page(self):
        return '/'

