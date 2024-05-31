from django.urls import path
from . import views

urlpatterns = [
    # ADMINISTRADOR
    path('administrador/logueo_administrador/', views.logueo_administrador, name='logueo_administrador'),
    path('administrador/dashboard_administrador/<int:id>/', views.dashboard_administrador, name='dashboard_administrador'),
    path('administrador/activar_cuenta/<int:id>/', views.activar_cuenta, name='activar_cuenta'),
    # Metodos Administrador
    # Vendedor
    path('administrador/vendedor/crear_vendedor/', views.crear_vendedor, name='crear_vendedor'),
    path('administrador/vendedor/eliminar_vendedor/<id>/', views.eliminar_vendedor, name='eliminar_vendedor'),
    path('administrador/vendedor/modificar_vendedor/<id>/', views.modificar_vendedor, name='modificar_vendedor'),
    path('administrador/vendedor/listar_vendedores/', views.listar_vendedores, name='listar_vendedores'),
    # Bodeguero
    path('administrador/bodeguero/crear_bodeguero/', views.crear_bodeguero, name='crear_bodeguero'),
    path('administrador/bodeguero/eliminar_bodeguero/<id>/', views.eliminar_bodeguero, name='eliminar_bodeguero'),
    path('administrador/bodeguero/modificar_bodeguero/<id>/', views.modificar_bodeguero, name='modificar_bodeguero'),
    path('administrador/bodeguero/listar_bodegueros/', views.listar_bodegueros, name='listar_bodegueros'),
    # Contador
    path('administrador/contador/crear_contador/', views.crear_contador, name='crear_contador'),
    path('administrador/contador/eliminar_contador/<id>/', views.eliminar_contador, name='eliminar_contador'),
    path('administrador/contador/modificar_contador/<id>/', views.modificar_contador, name='modificar_contador'),
    path('administrador/contador/listar_contadores/', views.listar_contadores, name='listar_contadores'),


    # Usuarios
    # CLIENTE
    path('', views.index_cliente, name='index_cliente'),
    path('cliente/producto_individual/<int:id>/', views.producto_individual, name='producto_individual'),
    path('cliente/carrito/', views.carrito, name='carrito'),
    path('cliente/logueo_cliente/', views.logueo_cliente, name='logueo_cliente'),
    path('cliente/register_cliente/', views.register_cliente, name='register_cliente'),
    path('cliente/catalogo_productos/', views.catalogo_productos, name='catalogo_productos'),
    # Filtros pagina Cliente de los Productos INDEX
    path('todos/', views.productos_todos, name='productos_todos'),
    path('mas-vendidos/', views.productos_mas_vendidos, name='productos_mas_vendidos'),
    path('nuevos/', views.productos_nuevos, name='productos_nuevos'),
    # VENDEDOR
    path('vendedor/logueo_vendedor/', views.logueo_vendedor, name='logueo_vendedor'),
    path('vendedor/index_vendedor/', views.index_vendedor, name='index_vendedor'),
    # BODEGUERO
    path('bodeguero/logueo_bodeguero/', views.logueo_bodeguero, name='logueo_bodeguero'),
    path('bodeguero/index_bodeguero/', views.index_bodeguero, name='index_bodeguero'),
    path('bodeguero/actualizar_stock/<int:producto_id>/', views.actualizar_stock, name='actualizar_stock'),
    path('pedidos/', views.listar_pedidos, name='listar_pedidos'),
    path('pedidos/confirmar/<int:pedido_id>/', views.confirmar_pedido, name='confirmar_pedido'),
    path('pedidos/entregar/<int:pedido_id>/', views.entregar_pedido, name='entregar_pedido'),
    # CONTADOR
    path('contador/logueo_contador/', views.logueo_contador, name='logueo_contador'),
    path('contador/index_contador/', views.index_contador, name='index_contador'),
    path('confirmar_pago/<int:compra_id>/', views.confirmar_pago, name='confirmar_pago'),
    path('rechazar_pago/<int:compra_id>/', views.rechazar_pago, name='rechazar_pago'),
    path('registrar_entrega/', views.registrar_entrega, name='registrar_entrega'),
    # Rutas de cierre de sesión
    path('administrador/logout/', views.cerrar_sesion_administrador, name='cerrar_sesion_administrador'),
    path('vendedor/logout/', views.cerrar_sesion_vendedor, name='cerrar_sesion_vendedor'),
    path('cliente/logout/', views.cerrar_sesion_cliente, name='cerrar_sesion_cliente'),
    path('bodeguero/logout/', views.cerrar_sesion_bodeguero, name='cerrar_sesion_bodeguero'),
    path('contador/logout/', views.cerrar_sesion_contador, name='cerrar_sesion_contador'),
]