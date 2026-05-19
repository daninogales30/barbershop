from datetime import datetime, timedelta, date, time

from django import forms

from reservas.models import Reserva


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


def generar_slots(fecha):
    inicio = time(9, 0)
    fin = time(21, 0)
    intervalo = timedelta(minutes=30)
    ahora = datetime.now().time()
    slots = []

    # Generar todas las posibles horas del día
    slot = inicio
    while slot <= fin:
        slots.append(slot)
        slot = (datetime.combine(fecha, slot) + intervalo).time()

    # Si la fecha es hoy, eliminar horas pasadas
    if fecha == datetime.now().date():
        slots = [s for s in slots if s > ahora]

    # Eliminar horas ya reservadas (para esta fecha)
    reservadas = Reserva.objects.filter(fecha=fecha).values_list('hora', flat=True)
    slots = [s for s in slots if s not in reservadas]

    return slots


class ReservaForm(forms.ModelForm):
    # Campo hora como ChoiceField con opciones dinámicas
    hora = forms.ChoiceField(choices=[], label="Hora")

    class Meta:
        model = Reserva
        fields = ['fecha', 'hora', 'tipo_corte', 'telefono', 'notas']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}),
            'tipo_corte': forms.Select(attrs={'class': 'campo'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Ej: 612345678', 'class': 'campo'}),
            'notas': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Indicaciones especiales...', 'class': 'campo-mensaje'}),
        }
        labels = {
            'tipo_corte': 'Servicio',
            'telefono': 'Teléfono de contacto',
            'notas': 'Notas adicionales (opcional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Obtener fecha del POST o del initial
        fecha_valor = self.data.get('fecha') or self.initial.get('fecha')
        if fecha_valor:
            # Si ya es un objeto date, lo usamos directamente
            if isinstance(fecha_valor, date):
                fecha = fecha_valor
            else:
                try:
                    fecha = datetime.strptime(fecha_valor, "%Y-%m-%d").date()
                except ValueError:
                    fecha = None
        else:
            fecha = None

        # Generar slots disponibles si hay fecha
        if fecha:
            slots = generar_slots(fecha)
            self.fields['hora'].choices = [(s.strftime("%H:%M"), s.strftime("%H:%M")) for s in slots]
            # Si el slot actual ya no está disponible, limpiar el valor
            if self.initial.get('hora'):
                hora_inicial = self.initial['hora'].strftime("%H:%M") if isinstance(self.initial['hora'], time) else \
                self.initial['hora']
                if hora_inicial not in [s.strftime("%H:%M") for s in slots]:
                    self.initial.pop('hora', None)
        else:
            self.fields['hora'].choices = []

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']
        if fecha < date.today():
            raise forms.ValidationError("No puedes reservar en el pasado.")
        if fecha.weekday() > 4:  # 5=sábado, 6=domingo
            raise forms.ValidationError("Solo abrimos de lunes a viernes.")
        return fecha

    def clean_hora(self):
        hora_str = self.cleaned_data['hora']
        fecha = self.cleaned_data.get('fecha')
        if not fecha:
            return hora_str

        # Validar que la hora esté en la lista de slots disponibles
        slots_disponibles = generar_slots(fecha)
        horas_validas = [s.strftime("%H:%M") for s in slots_disponibles]
        if hora_str not in horas_validas:
            raise forms.ValidationError("La hora seleccionada no está disponible.")
        return hora_str

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono:
            raise forms.ValidationError("El teléfono es obligatorio.")
        if not telefono.isdigit():
            raise forms.ValidationError("El teléfono debe contener solo números.")
        if len(telefono) < 9:
            raise forms.ValidationError("El teléfono debe tener al menos 9 dígitos.")
        return telefono

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha')
        hora_str = cleaned_data.get('hora')

        if fecha and hora_str:
            hora_obj = datetime.strptime(hora_str, "%H:%M").time()
            # Si es hoy, comprobar que no sea una hora ya pasada
            if fecha == date.today():
                ahora = datetime.now().time()
                if hora_obj <= ahora:
                    raise forms.ValidationError("No puedes reservar una hora que ya ha pasado.")
        return cleaned_data


class ContactoForm(forms.Form):
    nombre = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Tu Nombre'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Tu Email'}))
    asunto = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Asunto'}))
    mensaje = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Tu Mensaje'}))
