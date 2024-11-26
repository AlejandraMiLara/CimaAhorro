from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse
from .models import Fecha
from .forms import FechaForm, CustomUserCreationForm, TandaForm, SimuladorPrestamoForm, SolicitudPrestamoForm, AbonoForm, AhorroForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from decimal import Decimal
import os
from datetime import datetime, timedelta


solicitudes_prestamo_data = []
tandas_data = []
abonos_data = []
ahorros_data = []

def cargar_ahorros():
    global ahorros_data
    ahorros_data = []
    if os.path.exists('ahorros.txt'):
        with open('ahorros.txt', 'r') as file:
            for line in file:
                ahorro = line.strip().split()
                ahorros_data.append({
                    'id_usuario': ahorro[0],
                    'id_ahorro': ahorro[1],
                    'cantidad': Decimal(ahorro[2]),
                    'fecha': ahorro[3],
                })


def cargar_abonos():
    global abonos_data
    abonos_data = []
    if os.path.exists('abonos.txt'):
        with open('abonos.txt', 'r') as file:
            for line in file:
                abonos_data.append(line.strip().split())

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
    return tandas_data  # Asegurarnos de devolver siempre una lista

def cargar_inscripciones():
    inscripciones = {}
    if os.path.exists('inscripciones_tandas.txt'):
        with open('inscripciones_tandas.txt', 'r') as file:
            for line in file:
                user_id, tanda_id = line.strip().split()
                if tanda_id not in inscripciones:
                    inscripciones[tanda_id] = []
                inscripciones[tanda_id].append(user_id)
    return inscripciones

def cargar_pagos_tandas():
    pagos = {}
    if os.path.exists('pagos_tandas.txt'):
        with open('pagos_tandas.txt', 'r') as file:
            for line in file:
                user_id, tanda_id, cantidad_por_semana, fecha_pago = line.strip().split(',')
                if user_id not in pagos:
                    pagos[user_id] = []
                pagos[user_id].append({
                    'tanda_id': int(tanda_id),
                    'cantidad_por_semana': float(cantidad_por_semana),
                    'fecha_pago': datetime.strptime(fecha_pago, '%Y-%m-%d').date()
                })
    return pagos

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
                        fecha_liberacion = datos[9]

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
cargar_abonos()
cargar_ahorros()
cargar_inscripciones()
cargar_pagos_tandas()

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

            max_id = 0
            if os.path.exists('solicitudes_prestamo.txt'):
                with open('solicitudes_prestamo.txt', 'r') as file:
                    for line in file:
                        current_id = int(line.split()[0])
                        if current_id > max_id:
                            max_id = current_id
            id_solicitud = max_id + 1

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

        max_id = 0
        if os.path.exists('prestamos_aceptados.txt'):
            with open('prestamos_aceptados.txt', 'r') as file:
                for line in file:
                    current_id = int(line.split()[0])
                    if current_id > max_id:
                        max_id = current_id

        with open('prestamos_aceptados.txt', 'a') as file:
            for index in seleccionados:
                index = int(index)
                solicitud = solicitudes_prestamo_data[index]
                
                id_solicitud = max_id + 1
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

@login_required
def ver_prestamos(request):
    prestamos_del_usuario = [
        prestamo for prestamo in prestamos_aceptados_data if prestamo[1] == request.user.id
    ]

    if request.method == 'POST':
        prestamos_para_liberar = request.POST.getlist('liberar_recursos')
        fecha_reciente = Fecha.objects.order_by('-id').first()
        fecha_actual = fecha_reciente.fecha if fecha_reciente else timezone.now().date() 

        with open('prestamos_aceptados.txt', 'r') as file:
            lines = file.readlines()

        with open('prestamos_aceptados.txt', 'w') as file:
            for line in lines:
                datos = line.strip().split()
                if datos[0] in prestamos_para_liberar:
                    datos[7] = 'True' 
                    datos[9] = str(fecha_actual)
                file.write(" ".join(datos) + "\n")

        cargar_prestamos_aceptados()

        return redirect('ver_prestamos')

    cargar_prestamos_aceptados()

    return render(request, 'ver_prestamos.html', {
        'prestamos': prestamos_del_usuario
    })

@login_required
def abonar(request, id):
    global prestamos_aceptados_data
    cargar_prestamos_aceptados() 
    cargar_abonos() 

    id_str = str(id)
    user_id_str = str(request.user.id)

    prestamo = next((p for p in prestamos_aceptados_data if str(p[0]) == id_str and str(p[1]) == user_id_str), None)

    if not prestamo:
        return redirect('ver_prestamos')

    monto_total_pagar = float(prestamo[5])

    total_abonado = sum(float(a[2]) for a in abonos_data if a[0] == id_str and a[1] == user_id_str)
    resta_abonar = monto_total_pagar - total_abonado

    msj = ""

    if request.method == 'POST':
        form = AbonoForm(request.POST)
        if form.is_valid():
            monto_abono = form.cleaned_data['monto_abono']

            if monto_abono > resta_abonar:
                msj = "No puedes abonar más de la deuda actual."
            else:
                fecha_abono = timezone.now().date()

                with open('abonos.txt', 'a') as file:
                    file.write(f"{id} {request.user.id} {monto_abono} {fecha_abono}\n")

                cargar_abonos()
                msj = "Abono registrado correctamente."
                return redirect('ver_prestamos')
    else:
        form = AbonoForm()

    return render(request, 'abonar.html', {
        'form': form,
        'prestamo': prestamo,
        'total_abonado': total_abonado,
        'resta_abonar': resta_abonar,
        'msj': msj,
    })

@login_required
def historial_pagos(request, id):
    global prestamos_aceptados_data
    cargar_prestamos_aceptados() 
    cargar_abonos() 

    id_str = str(id)
    user_id_str = str(request.user.id)

    prestamo = next((p for p in prestamos_aceptados_data if str(p[0]) == id_str and str(p[1]) == user_id_str), None)
    
    if not prestamo:
        return redirect('ver_prestamos')

    pagos = [a for a in abonos_data if str(a[0]) == id_str and str(a[1]) == user_id_str]

    total_abonado = sum(float(a[2]) for a in pagos)
    resta_abonar = float(prestamo[5]) - total_abonado

    return render(request, 'historial_pagos.html', {'prestamo': prestamo, 'pagos': pagos, 'total_abonado': total_abonado, 'resta_abonar': resta_abonar})

@login_required
def simulador_ahorro(request):
    monto_ahorro = None
    total_a_dar = None
    acumulado = []

    if request.method == 'POST':
        # Recibir los datos del formulario
        monto_ahorro = Decimal(request.POST.get('monto_ahorro'))
        duracion_ahorro = request.POST.get('duracion_ahorro')

        # Determinar el interés y la duración en semanas
        if duracion_ahorro == 'semana':
            semanas = 1
            interes = Decimal('0.01')  # 1% semanal
        elif duracion_ahorro == 'mes':
            semanas = 4
            interes = Decimal('0.05')  # 5% mensual
        elif duracion_ahorro == 'bimestre':
            semanas = 8
            interes = Decimal('0.08')  # 8% bimestral
        else:  # semestre
            semanas = 24
            interes = Decimal('0.15')  # 15% semestral

        total_interes = monto_ahorro * interes
        total_a_dar = monto_ahorro + total_interes

        saldo_acumulado = Decimal('0.00')
        incremento_semanal = total_a_dar / semanas

        for semana in range(1, semanas + 1):
            saldo_acumulado += incremento_semanal

            acumulado.append({
                'semana': semana,
                'saldo_acumulado': round(saldo_acumulado, 2)
            })

    return render(request, 'simulador_ahorro.html', {
        'monto_ahorro': monto_ahorro,
        'total_a_dar': round(total_a_dar, 2) if total_a_dar else None,
        'acumulado': acumulado
    })
    
@login_required
def comenzar_ahorro(request):
    if request.method == 'POST':
        form = AhorroForm(request.POST)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad_ahorrar']
            id_usuario = str(request.user.id)
            fecha = str(timezone.now().date())

            max_id = 0
            if os.path.exists('ahorros.txt'):
                with open('ahorros.txt', 'r') as file:
                    for line in file:
                        current_id = int(line.split()[1])
                        if current_id > max_id:
                            max_id = current_id
            id_ahorro = max_id + 1

            with open('ahorros.txt', 'a') as file:
                file.write(f"{id_usuario} {id_ahorro} {cantidad} {fecha}\n")

            cargar_ahorros()
            return redirect('mis_ahorros')

    else:
        form = AhorroForm()

    return render(request, 'comenzar_ahorro.html', {'form': form})


@login_required
def retirar_ahorro(request):
    id_usuario = str(request.user.id)

    ahorros_usuario = [ahorro for ahorro in ahorros_data if ahorro['id_usuario'] == id_usuario]
    total_ahorrado = sum(ahorro['cantidad'] for ahorro in ahorros_usuario)
    puede_retirar = total_ahorrado > 0

    if request.method == 'POST' and puede_retirar:
        if os.path.exists('ahorros.txt'):
            with open('ahorros.txt', 'r') as file:
                lines = file.readlines()

            with open('ahorros.txt', 'w') as file:
                for line in lines:
                    if line.split()[0] != id_usuario:
                        file.write(line)

        cargar_ahorros()
        return redirect('mis_ahorros')
    
    if not puede_retirar:
        return render(request, 'retirar_ahorro.html', {
            'puede_retirar': puede_retirar,
            'msj': 'No puedes retirar si no has ahorrado'
        })

    return render(request, 'retirar_ahorro.html', {
        'puede_retirar': puede_retirar,
        'msj': '',
        'total_ahorrado': total_ahorrado,
    })



@login_required
def mis_ahorros(request):
    cargar_ahorros()
    id_usuario = str(request.user.id)
    ahorros_usuario = [ahorro for ahorro in ahorros_data if ahorro['id_usuario'] == id_usuario]
    total_ahorrado = sum(ahorro['cantidad'] for ahorro in ahorros_usuario)

    return render(request, 'mis_ahorros.html', {
        'ahorros': ahorros_usuario,
        'total_ahorrado': total_ahorrado
    })

@login_required
def unirse_a_tanda(request):
    global tandas_data
    cargar_tandas()

    # Cargar las inscripciones actuales
    inscripciones_actuales = cargar_inscripciones()

    mensaje = None  # Inicializar mensaje para mostrar al usuario

    if request.method == 'POST':
        id_tanda = int(request.POST.get('id_tanda'))
        user_id = str(request.user.id)

        # Buscar la tanda en la lista
        tanda_seleccionada = next((tanda for tanda in tandas_data if tanda['id_tanda'] == id_tanda), None)

        if tanda_seleccionada:
            # Asegurarse de que la clave 'usuarios_inscritos' exista
            if 'usuarios_inscritos' not in tanda_seleccionada:
                tanda_seleccionada['usuarios_inscritos'] = []

            # Obtener las inscripciones actuales de la tanda
            inscripciones_en_tanda = inscripciones_actuales.get(str(id_tanda), [])
            usuarios_inscritos = len(inscripciones_en_tanda) + len(tanda_seleccionada['usuarios_inscritos'])

            # Verificar si el usuario ya está inscrito en la tanda
            if user_id in tanda_seleccionada['usuarios_inscritos'] or user_id in inscripciones_en_tanda:
                mensaje = "Ya estás inscrito en esta tanda."
            else:
                # Verificar si la tanda tiene espacio para más usuarios
                max_estudiantes = tanda_seleccionada['estudiantes']

                # Si la cantidad de usuarios inscritos es menor al máximo
                if usuarios_inscritos < max_estudiantes:
                    # Registrar la inscripción en memoria y en el archivo
                    tanda_seleccionada['usuarios_inscritos'].append(user_id)
                    if str(id_tanda) not in inscripciones_actuales:
                        inscripciones_actuales[str(id_tanda)] = []
                    inscripciones_actuales[str(id_tanda)].append(user_id)

                    # Guardar la inscripción del usuario en inscripciones_tandas.txt
                    with open('inscripciones_tandas.txt', 'a') as file:
                        file.write(f"{user_id} {id_tanda}\n")

                    # Actualizar el archivo de tandas
                    with open('tandas.txt', 'w') as file:
                        for tanda in tandas_data:
                            usuarios = ','.join(tanda.get('usuarios_inscritos', []))  # Convertir a string para guardar
                            file.write(f"{tanda['id_tanda']} {tanda['estudiantes']} {tanda['cantidad_por_semana']} "
                                       f"{tanda['cantidad_acumulada']} {tanda['duracion']} {tanda['estado']} "
                                       f"{tanda['interes_ganado']}\n")

                    # Recargar los datos actualizados
                    cargar_tandas()

                    mensaje = "Te has unido con éxito a la tanda."
                else:
                    mensaje = "Esta tanda ya ha alcanzado el número máximo de estudiantes."

        else:
            mensaje = "La tanda seleccionada no existe."

    return render(request, 'unirse_a_tanda.html', {
        'tandas': [tanda for tanda in tandas_data if tanda['estado'] == 1],  # Solo mostrar tandas activas
        'mensaje': mensaje  # Mostrar el mensaje en la página
    })
    
@login_required
def pagar_tanda(request):
    error = None
    tandas = cargar_tandas()  # Cargar todas las tandas
    inscripciones = cargar_inscripciones()  # Cargar las inscripciones
    pagos = cargar_pagos_tandas()  # Cargar los pagos realizados
    usuario_id = str(request.user.id)  # Obtener el ID del usuario logueado
    
    # Obtener la fecha del panel
    fecha_reciente = Fecha.objects.order_by('-id').first()
    fecha_a_mostrar = fecha_reciente.fecha if fecha_reciente else timezone.now().date()

    # Inicializar la lista de tandas pendientes
    tandas_pendientes = []
    
    # Filtrar las tandas en las que el usuario está inscrito y no ha pagado esta semana
    for tanda in tandas:
        # Verificar si el usuario está inscrito en esta tanda
        if usuario_id in inscripciones.get(str(tanda['id_tanda']), []):
            # Verificar si el usuario ya pagó en la última semana
            pagos_usuario = pagos.get(usuario_id, [])
            ultimo_pago = max([pago for pago in pagos_usuario if pago['tanda_id'] == tanda['id_tanda']], 
                              key=lambda x: x['fecha_pago'], default=None)
            
            # Si el usuario ya pagó esta semana, no mostrar esta tanda
            if ultimo_pago and (fecha_a_mostrar - ultimo_pago['fecha_pago']).days < 7:
                continue  # Si ya pagó esta semana, saltamos esta tanda
            
            # Si no ha pagado, la agregamos a la lista de pendientes
            tandas_pendientes.append(tanda)

    if request.method == 'POST':
        id_tanda = int(request.POST.get('id_tanda'))
        monto_pagado = float(request.POST.get('monto_pagado'))

        # Verificar si el monto es correcto (debería ser la cantidad semanal)
        tanda_a_pagar = next((tanda for tanda in tandas_pendientes if tanda['id_tanda'] == id_tanda), None)
        if tanda_a_pagar:
            if monto_pagado != tanda_a_pagar['cantidad_por_semana']:
                error = "El monto a pagar no es correcto."
            else:
                # Registrar el pago en el archivo pagos_tandas.txt con la fecha del panel
                try:
                    with open('pagos_tandas.txt', 'a') as file:
                        file.write(f"{usuario_id},{id_tanda},{monto_pagado},{fecha_a_mostrar}\n")
                    # Actualizar el acumulado
                    tanda_a_pagar['cantidad_acumulada'] += monto_pagado
                    return redirect('pagar_tanda')  # Redirigir después de pagar
                except Exception as e:
                    error = f"Ocurrió un error al registrar el pago: {e}"

    return render(request, 'pagar_tanda.html', {'tandas_pendientes': tandas_pendientes, 'error': error, 'fecha_a_mostrar': fecha_a_mostrar})

def historial_pagos_tandas(request):
    usuario_id = str(request.user.id)  
    pagos = cargar_pagos_tandas()  
    tandas = cargar_tandas()  
    historial = []

    if usuario_id in pagos:
        for pago in pagos[usuario_id]:
            # Buscar la información de la tanda relacionada con el pago
            tanda = next((t for t in tandas if t['id_tanda'] == pago['tanda_id']), None)
            if tanda:
                historial.append({
                    'tanda_id': pago['tanda_id'],
                    'cantidad_por_semana': pago['cantidad_por_semana'],
                    'fecha_pago': pago['fecha_pago'],
                    'estado': 'Pagado' if tanda['estado'] == 1 else 'Inactivo'
                })

    return render(request, 'historial_pagos_tandas.html', {'historial': historial})

@login_required
def informacion_tandas_actuales(request):
    tandas = cargar_tandas()  # Cargar todas las tandas
    inscripciones = cargar_inscripciones()  # Cargar las inscripciones
    
    # Obtener el ID del usuario logueado
    usuario_id = str(request.user.id)

    # Inicializar la lista de tandas en las que el usuario está inscrito
    tandas_usuario = []
    
    # Filtrar las tandas en las que el usuario está inscrito
    for tanda in tandas:
        if usuario_id in inscripciones.get(str(tanda['id_tanda']), []):
            # Contar la cantidad de usuarios inscritos en esta tanda
            cantidad_usuarios = len(inscripciones.get(str(tanda['id_tanda']), []))
            tanda['cantidad_usuarios'] = cantidad_usuarios  # Agregar el dato a la tanda
            tandas_usuario.append(tanda)

    return render(request, 'informacion_tandas_actuales.html', {'tandas': tandas_usuario})
