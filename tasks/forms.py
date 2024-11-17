from django import forms
from .models import Fecha
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

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
