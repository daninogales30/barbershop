from django.urls import path
from .views import HomeView, ServiciosView, ContactosView, SomosView, ReservaCreateView, horas_disponibles_api

app_name = 'reservas'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('servicios/', ServiciosView.as_view(), name='servicios'),
    path('contacto/', ContactosView.as_view(), name='contactos'),
    path('quienes_somos/', SomosView.as_view(), name='somos'),
    path('crear_reserva/', ReservaCreateView.as_view(), name='crear_reserva'),
    path('horas-disponibles/', horas_disponibles_api, name='horas_disponibles'),
]
