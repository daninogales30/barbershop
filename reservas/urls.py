from django.urls import path
from .views import HomeView, ServiciosView, ContactosView, SomosView, RegisterView, ReservaCreateView, CustomLogoutView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('servicios/', ServiciosView.as_view(), name='servicios'),
    path('contacto/', ContactosView.as_view(), name='contactos'),
    path('quienes_somos/', SomosView.as_view(), name='somos'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('crear_reserva/', ReservaCreateView.as_view(), name='crear_reserva'),
]