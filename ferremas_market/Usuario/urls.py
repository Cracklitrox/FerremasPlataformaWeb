from django.urls import path
from . import views

urlpatterns = [
    # ADMINISTRADOR
    path('administrador/logueo_administrador/', views.logueo_administrador, name='logueo_administrador'),
    path('administrador/dashboard_administrador/', views.dashboard_administrador, name='dashboard_administrador'),
    # path('administrador/activar_cuenta/<int:id>/', views.activar_cuenta, name='activar_cuenta')
    # CLIENTE
    path('cliente/index_cliente/', views.index_cliente, name='index_cliente'),
]