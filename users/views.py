from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import FormView, DetailView

from reservas.models import Reserva
from reservas.services import send_verification_email
from users.forms import LoginForm, RegistroForm
from users.models import User


class PerfilView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/perfil.html'
    context_object_name = 'usuario'

    def get_object(self):
        # Muestra el perfil del usuario logueado
        return self.request.user

    def get_context_data(self, **kwargs):
        from reservas.services import marcar_reservas_completadas

        marcar_reservas_completadas()

        context = super().get_context_data(**kwargs)
        user = self.get_object()
        # Lista de reservas del usuario (ordenadas por fecha descendente)
        context['reservas'] = Reserva.objects.filter(usuario=user).order_by('-fecha', '-hora')
        # Estadísticas adicionales (opcional)
        context['total_citas'] = Reserva.objects.filter(usuario=user).count()
        context['pendientes'] = Reserva.objects.filter(usuario=user, estado='pendiente').count()
        return context

    def post(self, request, *args, **kwargs):
        user = self.get_object()

        if 'foto_perfil' in request.FILES:
            user.foto_perfil = request.FILES['foto_perfil']
            user.save()

            messages.success(request, "Foto de perfil actualizada correctamente.")

        return redirect('users:perfil')

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
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1'],
            nombre=form.cleaned_data['nombre'],
            apellidos=form.cleaned_data['apellidos'],
            fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento'),
        )

        user.is_active = False

        if 'foto_perfil' in self.request.FILES:
            user.foto_perfil = self.request.FILES['foto_perfil']

        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        link = self.request.build_absolute_uri(
            f"/activar/{uid}/{token}/"
        )

        send_verification_email(user.email, link)

        messages.success(
            self.request,
            "Te hemos enviado un correo para activar tu cuenta"
        )

        return redirect("users:login")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect("users:login")

    return redirect("users:register")

class CancelarReservaView(LoginRequiredMixin, View):

    def post(self, request, pk):

        reserva = get_object_or_404(
            Reserva,
            pk=pk,
            usuario=request.user
        )

        reserva.estado = "cancelado"
        reserva.save()

        return redirect("users:perfil")


