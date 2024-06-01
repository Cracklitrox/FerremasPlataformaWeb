from django.urls import path
from . import views

urlpatterns = [
    path('api/anular-compra/', views.anular_compra, name='anular_compra'),
    path('api/update-stock/', views.actualizar_stock, name='actualizar_stock'),
    path('iniciar-transaccion/', views.iniciar_transaccion, name='iniciar-transaccion'),
    path('confirmar-transaccion/', views.confirmar_transaccion, name='confirmar-transaccion'),
]