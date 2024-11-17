from django import forms
from .models import Fecha

class FechaForm(forms.ModelForm):
    class Meta:
        model = Fecha
        fields = ['fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }
