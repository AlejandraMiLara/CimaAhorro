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
]
