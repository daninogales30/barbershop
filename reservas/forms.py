from datetime import datetime, timedelta, date

from django import forms

from reservas.models import Reserva


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


def generar_slots(fecha=None):
    slots = []

    start = datetime.strptime("09:00", "%H:%M")
    end = datetime.strptime("21:00", "%H:%M")

    now = datetime.now()

    # 🔥 traer horas ya reservadas de ese día
    ocupadas = []

    if fecha:
        ocupadas = Reserva.objects.filter(fecha=fecha).values_list('hora', flat=True)

    while start < end:
        slot_time = start.time()

        # ❌ si está ocupada, no la mostramos
        if slot_time in ocupadas:
            start += timedelta(minutes=30)
            continue

        # ❌ si es hoy, no mostrar horas pasadas
        if fecha == date.today():
            if slot_time <= now.time():
                start += timedelta(minutes=30)
                continue

        slots.append(slot_time)
        start += timedelta(minutes=30)

    return slots


class ReservaForm(forms.ModelForm):
    hora = forms.ChoiceField(choices=[])

    class Meta:
        model = Reserva
        fields = ['fecha', 'hora']

        widgets = {
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'min': date.today().isoformat()  # 👈 clave
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fecha = self.data.get('fecha') or self.initial.get('fecha')

        if fecha:
            from datetime import datetime
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

        slots = generar_slots(fecha)

        self.fields['hora'].choices = [
            (s.strftime("%H:%M"), s.strftime("%H:%M"))
            for s in slots
        ]

    def clean_fecha(self):
        fecha = self.cleaned_data['fecha']

        if fecha < date.today():
            raise forms.ValidationError("No puedes reservar en el pasado")

        if fecha.weekday() > 4:
            raise forms.ValidationError("Solo abrimos de lunes a viernes")

        return fecha

    def clean_hora(self):
        hora = self.cleaned_data['hora']

        if hora not in [slot.strftime("%H:%M") for slot in generar_slots()]:
            raise forms.ValidationError("Hora no válida")

        return hora

    def clean(self):
        cleaned_data = super().clean()

        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')

        if not fecha or not hora:
            return cleaned_data

        # convertir hora string a objeto time
        hora_obj = datetime.strptime(hora, "%H:%M").time()

        ahora = datetime.now()

        # si es hoy, no permitir horas pasadas
        if fecha == date.today():
            if hora_obj < ahora.time():
                raise forms.ValidationError(
                    "No puedes reservar una hora que ya ha pasado"
                )

        return cleaned_data
