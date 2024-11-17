from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from .models import Fecha
from .forms import FechaForm, CustomUserCreationForm, TandaForm, SimuladorPrestamoForm, SolicitudPrestamoForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from decimal import Decimal
import os

solicitudes_prestamo_data = []
tandas_data = []
tandas_data = []

def cargar_solicitudes_prestamo():
    global solicitudes_prestamo_data
    solicitudes_prestamo_data = []

    if os.path.exists('solicitudes_prestamo.txt'):
        with open('solicitudes_prestamo.txt', 'r') as file:
            for line in file:
                solicitud = line.strip().split()
                solicitudes_prestamo_data.append({
                    'id_solicitud': solicitud[0],
                    'id_usuario': solicitud[1],
                    'matricula': solicitud[2],
                    'monto': solicitud[3],
                    'duracion': solicitud[4],
                    'monto_total': solicitud[5],
                    'acepto_intereses': solicitud[6],
                })

def cargar_tandas():
    global tandas_data
    tandas_data = []

    if os.path.exists('tandas.txt'):
        with open('tandas.txt', 'r') as file:
            for line in file:
                partes = line.strip().split()
                tanda = {
                    'id_tanda': int(partes[0]),
                    'estudiantes': int(partes[1]),
                    'cantidad_por_semana': float(partes[2]),
                    'cantidad_acumulada': float(partes[3]),
                    'duracion': int(partes[4]),
                    'estado': int(partes[5]),
                    'interes_ganado': float(partes[6])
                }
                tandas_data.append(tanda)

def cargar_prestamos_aceptados():
    global prestamos_aceptados_data
    prestamos_aceptados_data = []

    if os.path.exists('prestamos_aceptados.txt'):
        with open('prestamos_aceptados.txt', 'r') as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                datos = line.split()

                if len(datos) == 10:
                    try:
                        id_solicitud = int(datos[0])
                        id_usuario = int(datos[1])
                        matricula = datos[2]
                        monto = float(datos[3])
                        duracion = int(datos[4])
                        monto_total = float(datos[5])
                        acepta_intereses = datos[6] == 'True'
                        recursos_liberados = datos[7] == 'True'
                        fecha_aceptado = datos[8]
                        fecha_liberacion = int(datos[9])

                        prestamos_aceptados_data.append([id_solicitud, id_usuario, matricula, monto, duracion, monto_total,
                                                         acepta_intereses, recursos_liberados, fecha_aceptado, fecha_liberacion])
                    except ValueError as e:
                        print(f"Error al procesar la línea (valor incorrecto): {line}")
                        print(f"Error específico: {e}")
                        print(f"Datos problemáticos: {datos}")
                else:
                    print(f"Error: línea con formato incorrecto: {line}")

cargar_solicitudes_prestamo()
cargar_prestamos_aceptados()
cargar_tandas()


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

            cargar_tandas()
            return redirect('panel') 
    else:
        form = TandaForm()

    return render(request, 'abrir_tanda.html', {'form': form})

def simulador_prestamo(request):
    if request.method == 'POST':
        form = SimuladorPrestamoForm(request.POST)
        if form.is_valid():
            monto_prestamo = form.cleaned_data['monto_prestamo']
            duracion_prestamo = form.cleaned_data['duracion_prestamo']

            if duracion_prestamo == 'semana':
                semanas = 1
                interes = Decimal('0.01')
            elif duracion_prestamo == 'mes':
                semanas = 4
                interes = Decimal('0.05')
            elif duracion_prestamo == 'bimestre':
                semanas = 8
                interes = Decimal('0.08')
            else:  # semestre
                semanas = 24
                interes = Decimal('0.15')

            total_interes = monto_prestamo * interes
            total_a_pagar = monto_prestamo + total_interes
            pago_semanal = total_a_pagar / semanas

            amortizacion = []
            saldo_restante = total_a_pagar

            for semana in range(1, semanas + 1):
                saldo_restante -= pago_semanal
                if saldo_restante < 0:
                    saldo_restante = Decimal('0.00')

                amortizacion.append({
                    'semana': semana,
                    'pago': round(pago_semanal, 2),
                    'saldo_restante': round(saldo_restante, 2)
                })

            return render(request, 'simulador_prestamo.html', {
                'form': form,
                'monto_prestamo': monto_prestamo,
                'total_a_pagar': round(total_a_pagar, 2),
                'pago_semanal': round(pago_semanal, 2),
                'amortizacion': amortizacion
            })
    else:
        form = SimuladorPrestamoForm()

    return render(request, 'simulador_prestamo.html', {'form': form})

@login_required
def solicitud_prestamo(request):
    interes_dict = {
        'semana': Decimal('0.01'),
        'mes': Decimal('0.05'),
        'bimestre': Decimal('0.08'),
        'semestre': Decimal('0.15')
    }

    if request.method == 'POST':
        form = SolicitudPrestamoForm(request.POST)
        if form.is_valid():
            monto_prestamo = form.cleaned_data['monto_prestamo']
            duracion_prestamo = form.cleaned_data['duracion_prestamo']
            acepta_intereses = form.cleaned_data['acepta_intereses']
            matricula = form.cleaned_data['matricula']

            interes = interes_dict[duracion_prestamo]
            total_interes = monto_prestamo * interes
            total_a_pagar = monto_prestamo + total_interes

            if duracion_prestamo == 'semana':
                duracion = 1
            elif duracion_prestamo == 'mes':
                duracion = 4
            elif duracion_prestamo == 'bimestre':
                duracion = 8
            elif duracion_prestamo == 'semestre':
                duracion = 24

            id_usuario = request.user.id

            id_solicitud = sum(1 for line in open('solicitudes_prestamo.txt')) + 1

            with open('solicitudes_prestamo.txt', 'a') as file:
                file.write(f"{id_solicitud} {id_usuario} {matricula} {monto_prestamo} {duracion} {total_a_pagar} {acepta_intereses}\n")

            cargar_solicitudes_prestamo()
            return redirect('panel')

    else:
        form = SolicitudPrestamoForm()

    return render(request, 'solicitud_prestamo.html', {'form': form})


@login_required
def gestionar_prestamos(request):
    global solicitudes_prestamo_data

    if request.user.rol != 1:
        return redirect('inicio')

    cargar_solicitudes_prestamo()
    cargar_prestamos_aceptados()

    if request.method == 'POST':
        seleccionados = request.POST.getlist('seleccionados')
        nuevos_prestamos = []

        fecha_reciente = Fecha.objects.order_by('-id').first()
        fecha_aceptado = fecha_reciente.fecha if fecha_reciente else timezone.now().date()

        with open('prestamos_aceptados.txt', 'a') as file:
            for index in seleccionados:
                index = int(index)
                solicitud = solicitudes_prestamo_data[index]
                
                id_solicitud = solicitud['id_solicitud']
                id_usuario = solicitud['id_usuario']
                matricula = solicitud['matricula']
                monto = solicitud['monto']
                duracion = solicitud['duracion']
                monto_total = solicitud['monto_total']
                acepta_intereses = solicitud['acepto_intereses']
                
                recursos_liberados = False
                fecha_liberacion = 0 

                file.write(f"{id_solicitud} {id_usuario} {matricula} {monto} {duracion} {monto_total} {acepta_intereses} "
                           f"{recursos_liberados} {fecha_aceptado} {fecha_liberacion}\n")

                prestamos_aceptados_data.append([id_solicitud, id_usuario, matricula, monto, duracion, monto_total,
                                                 acepta_intereses, recursos_liberados, fecha_aceptado, fecha_liberacion])

        with open('solicitudes_prestamo.txt', 'r') as file:
            lines = file.readlines()

        with open('solicitudes_prestamo.txt', 'w') as file:
            for i, line in enumerate(lines):
                if i not in map(int, seleccionados):
                    file.write(line)

        cargar_solicitudes_prestamo()

    return render(request, 'gestionar_prestamos.html', {
        'solicitudes': solicitudes_prestamo_data,
        'prestamos_aceptados': prestamos_aceptados_data
    })

@login_required
def prestamos_aceptados(request):
    cargar_prestamos_aceptados()

    if request.user.rol != 1:
        return redirect('inicio')

    print(prestamos_aceptados_data)

    return render(request, 'prestamos_aceptados.html', {
        'prestamos_aceptados': prestamos_aceptados_data
    })

@login_required
def mis_solicitudes_prestamo(request):
    global solicitudes_prestamo_data

    solicitudes_estudiante = [solicitud for solicitud in solicitudes_prestamo_data if solicitud['id_usuario'] == str(request.user.id)]

    if request.method == 'POST':
        solicitudes_canceladas = request.POST.getlist('cancelar_solicitud')
        
        with open('solicitudes_prestamo.txt', 'r') as file:
            lines = file.readlines()

        with open('solicitudes_prestamo.txt', 'w') as file:
            for i, line in enumerate(lines):
                solicitud = line.strip().split()
                if solicitud[0] not in solicitudes_canceladas:
                    file.write(line)

        cargar_solicitudes_prestamo()
        
        return redirect('mis_solicitudes_prestamo')

    return render(request, 'mis_solicitudes_prestamo.html', {
        'solicitudes': solicitudes_estudiante
    })
