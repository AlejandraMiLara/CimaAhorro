from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from .models import Fecha
from .forms import FechaForm, CustomUserCreationForm, TandaForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def inicio(request):
    return render(request, 'inicio.html')

def registro(request):
    if request.method == 'GET':
        return render(request, 'registro.html', {'form': CustomUserCreationForm()})
    else:
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('panel')
        else:
            return render(request, 'registro.html', {'form': form})

def ingreso(request):

    if request.method == 'GET':
        return render(request, 'ingreso.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'ingreso.html', {
                'form': AuthenticationForm,
                'msj': 'Usuario o password incorrecto'
            })
        else:
            login(request, user)
            return redirect('panel')

def salir(request):
    logout(request)
    return redirect('ingreso')

def panel(request):
    fecha_reciente = Fecha.objects.order_by('-id').first()
    fecha_a_mostrar = fecha_reciente.fecha if fecha_reciente else timezone.now().date()

    if request.method == 'POST':
        form = FechaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('panel')
    else:
        form = FechaForm()

    return render(request, 'panel.html', {'form': form, 'fecha_a_mostrar': fecha_a_mostrar})


from decimal import Decimal

@login_required
def abrir_tanda(request):
    interes = Decimal('0.03')

    if request.user.rol != 1:
        return redirect('inicio')

    if request.method == 'POST':
        form = TandaForm(request.POST)
        if form.is_valid():
            id_tanda = form.cleaned_data['id_tanda']
            estudiantes = form.cleaned_data['estudiantes']
            cantidad_por_semana = form.cleaned_data['cantidad_por_semana']
            duracion_semanas = form.cleaned_data['duracion_semanas']

            cantidad_acumulada = (estudiantes * cantidad_por_semana) * duracion_semanas
            interes_ganado = cantidad_acumulada * interes

            with open('tandas.txt', 'a') as file:
                file.write(f"{id_tanda} {estudiantes} {cantidad_por_semana} {cantidad_acumulada} {duracion_semanas} {1} {interes_ganado}\n")

            return redirect('panel') 
    else:
        form = TandaForm()

    return render(request, 'abrir_tanda.html', {'form': form})
