from django.urls import path
from . import views

urlpatterns = [
    path('api/actualizar-stock/', views.actualizar_stock, name='actualizar_stock'),
    path('api/guardar-carrito/', views.guardar_carrito, name='guardar_carrito'),
    path('api/anadir-al-carrito/<int:product_id>/', views.anadir_al_carrito, name='anadir_al_carrito'),
    path('api/obtener-carrito/', views.obtener_carrito, name='obtener_carrito'),
    path('api/anular-compra/', views.anular_compra, name='anular_compra'),
    path('iniciar-transaccion/', views.iniciar_transaccion, name='iniciar-transaccion'),
    path('confirmar-transaccion/', views.confirmar_transaccion, name='confirmar-transaccion'),
]