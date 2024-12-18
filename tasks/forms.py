from django import forms
from .models import Fecha
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class AbonoForm(forms.Form):
    monto_abono = forms.DecimalField(max_digits=10, decimal_places=2, label='Monto a Abonar')

class FechaForm(forms.ModelForm):
    class Meta:
        model = Fecha
        fields = ['fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'rol']
        widgets = {
            'rol': forms.HiddenInput()
        }

class TandaForm(forms.Form):
    id_tanda = forms.IntegerField(label='ID de la Tanda')
    estudiantes = forms.IntegerField(label='Cantidad de Estudiantes')
    cantidad_por_semana = forms.DecimalField(label='Cantidad por Semana', max_digits=10, decimal_places=2)
    duracion_semanas = forms.IntegerField(label='Duración en Semanas')

class SimuladorPrestamoForm(forms.Form):
    monto_prestamo = forms.DecimalField(label='Monto del Préstamo', max_digits=10, decimal_places=2)
    duracion_prestamo = forms.ChoiceField(
        label='Duración del Préstamo',
        choices=[
            ('semana', '1 Semana'),
            ('mes', '1 Mes'),
            ('bimestre', 'Bimestre'),
            ('semestre', 'Semestre')
        ]
    )

class SolicitudPrestamoForm(forms.Form):
    matricula = forms.IntegerField(label='Matrícula')
    monto_prestamo = forms.DecimalField(label='Monto del Préstamo', max_digits=10, decimal_places=2)
    duracion_prestamo = forms.ChoiceField(
        label='Duración del Préstamo',
        choices=[
            ('semana', '1 Semana'),
            ('mes', '1 Mes'),
            ('bimestre', 'Bimestre'),
            ('semestre', 'Semestre')
        ]
    )
    acepta_intereses = forms.BooleanField(label='Acepto pagar los intereses del período', required=True)

class AhorroForm(forms.Form):
    cantidad_ahorrar = forms.DecimalField(label='Cantidad a Ahorrar', max_digits=10, decimal_places=2)
