from django.contrib import admin
from django.urls import path
from tasks import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('registro/', views.registro, name='registro'),
    path('ingreso/', views.ingreso, name='ingreso'),
    path('salir/', views.salir, name='salir'),
    path('panel/', views.panel, name='panel'),
    path('abrir_tanda/', views.abrir_tanda, name='abrir_tanda'),
    path('simulador_prestamo/', views.simulador_prestamo, name='simulador_prestamo'),
    path('solicitud_prestamo/', views.solicitud_prestamo, name='solicitud_prestamo'),
    path('gestionar_prestamos/', views.gestionar_prestamos, name='gestionar_prestamos'),
    path('prestamos_aceptados/', views.prestamos_aceptados, name='prestamos_aceptados'),
    path('mis_solicitudes/', views.mis_solicitudes_prestamo, name='mis_solicitudes_prestamo'),
    path('ver_prestamos/', views.ver_prestamos, name='ver_prestamos'),
    path('abonar/<int:id>/', views.abonar, name='abonar'),
    path('historial_pagos/<int:id>/', views.historial_pagos, name='historial_pagos'),
    path('comenzar_ahorro/', views.comenzar_ahorro, name='comenzar_ahorro'),
    path('retirar_ahorro/', views.retirar_ahorro, name='retirar_ahorro'),
    path('mis_ahorros/', views.mis_ahorros, name='mis_ahorros'),
    path('unirse_a_tanda/', views.unirse_a_tanda, name='unirse_a_tanda'),
]
