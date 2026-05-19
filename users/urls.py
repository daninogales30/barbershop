from django.urls import path
from django.contrib.auth.views import LogoutView

from users.views import PerfilView, LoginView

app_name = 'users'

urlpatterns = [
    path('perfil/', PerfilView.as_view(), name='perfil'),
    path('login/', LoginView.as_view(), name='login'),
    path("logout/", LogoutView.as_view(next_page="reservas:home"), name="logout")
]
