from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView

from reservas.models import Reserva
from users.forms import LoginForm, RegistroForm
from users.models import User


class PerfilView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/perfil.html'
    context_object_name = 'usuario'

    def get_context_data(self, **kwargs):
        from reservas.services import marcar_reservas_expiradas

        marcar_reservas_expiradas()


    def get_object(self):
        # Muestra el perfil del usuario logueado
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        # Lista de reservas del usuario (ordenadas por fecha descendente)
        context['reservas'] = Reserva.objects.filter(usuario=user).order_by('-fecha', '-hora')
        # Estadísticas adicionales (opcional)
        context['total_citas'] = Reserva.objects.filter(usuario=user).count()
        context['pendientes'] = Reserva.objects.filter(usuario=user, estado='pendiente').count()
        return context

class LoginView(FormView):
    template_name = 'registration/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('reservas:home')  # fallback

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)

            next_url = self.request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return super().form_valid(form)

        messages.error(self.request, 'Credenciales incorrectas')
        return super().form_invalid(form)

class RegistroView(FormView):
    template_name = 'registration/register.html'
    form_class = RegistroForm
    success_url = reverse_lazy('reservas:home')

    def form_valid(self, form):
        # Crear usuario manualmente con los datos del formulario
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1'],
            nombre=form.cleaned_data['nombre'],
            apellidos=form.cleaned_data['apellidos'],
            fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento')
        )
        login(self.request, user)
        return super().form_valid(form)


