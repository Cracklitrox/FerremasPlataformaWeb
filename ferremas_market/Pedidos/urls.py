from django.urls import path
from . import views

urlpatterns = [
    path('agregar_al_carrito/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('vaciar_carrito/', views.vaciar_carrito, name='vaciar_carrito'),
]