from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse

def inicio(request):
    return render(request, 'inicio.html')

def registro(request):

    if request.method == 'GET':
        return render(request, 'registro.html', {
            'form':UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('panel')
            except:
                return render(request, 'registro.html', {
                    'form':UserCreationForm,
                    'msj': 'El nombre de usuario ya existe'
                })
            
        else:
            return render(request, 'registro.html', {
                'form':UserCreationForm,
                'msj': 'Los passwords no son iguales'
            })

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
    return render(request, 'panel.html')