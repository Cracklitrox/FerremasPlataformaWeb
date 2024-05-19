from django.urls import path
from . import views

urlpatterns = [
    # ADMINISTRADOR
    path('administrador/logueo_administrador/', views.logueo_administrador, name='logueo_administrador'),
    path('administrador/dashboard_administrador/<int:id>/', views.dashboard_administrador, name='dashboard_administrador'),
    path('administrador/activar_cuenta/<int:id>/', views.activar_cuenta, name='activar_cuenta'),
    # Metodos Administrador
    path('administrador/vendedor/crear_vendedor/', views.crear_vendedor, name='crear_vendedor'),
    path('administrador/vendedor/eliminar_vendedor/<id>/', views.eliminar_vendedor, name='eliminar_vendedor'),
    path('administrador/vendedor/modificar_vendedor/<id>/', views.modificar_vendedor, name='modificar_vendedor'),
    path('administrador/vendedor/listar_vendedores/', views.listar_vendedores, name='listar_vendedores'),
    # CLIENTE
    path('', views.index_cliente, name='index_cliente'),
    path('cliente/logueo_cliente/', views.logueo_cliente, name='logueo_cliente'),
    path('cliente/register_cliente/', views.register_cliente, name='register_cliente'),
    # VENDEDOR
    path('vendedor/logueo_vendedor/', views.logueo_vendedor, name='logueo_vendedor'),
    path('vendedor/index_vendedor/', views.index_vendedor, name='index_vendedor'),
    # Rutas de cierre de sesión
    path('administrador/logout/', views.cerrar_sesion_administrador, name='cerrar_sesion_administrador'),
    path('vendedor/logout/', views.cerrar_sesion_vendedor, name='cerrar_sesion_vendedor'),
    path('cliente/logout/', views.cerrar_sesion_cliente, name='cerrar_sesion_cliente'),
    path('bodeguero/logout/', views.cerrar_sesion_bodeguero, name='cerrar_sesion_bodeguero'),
    path('contador/logout/', views.cerrar_sesion_contador, name='cerrar_sesion_contador'),
]