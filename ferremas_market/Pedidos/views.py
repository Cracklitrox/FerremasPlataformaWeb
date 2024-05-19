import datetime
from functools import wraps
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import *

# Create your views here.

##################################
##            Carrito           ##
##################################

def agregar_al_carrito(request):
    if not request.session.get('is_cliente_logged_in'):
        return JsonResponse({'error': 'Debes iniciar sesión para agregar productos al carrito.'}, status=403)

    producto_id = request.POST.get('producto_id')
    producto = get_object_or_404(Producto, id=producto_id)

    usuario = request.user
    cliente = get_object_or_404(Cliente, usuario_ptr_id=usuario.id)

    carrito, creado = Carrito.objects.get_or_create(run=cliente, activo=True)

    producto_carrito, creado = ProductoCarrito.objects.get_or_create(carrito=carrito, producto=producto)
    if not creado:
        if producto_carrito.cantidad < producto.stock:
            producto_carrito.cantidad += 1
        else:
            return JsonResponse({'error': 'No puedes agregar más de este producto, stock limitado.'}, status=400)
    producto_carrito.save()

    carrito.hora_actualizado = timezone.now()
    carrito.save()

    return JsonResponse({'mensaje': 'Producto agregado al carrito.'}, status=200)

def vaciar_carrito(request):
    if not request.session.get('is_cliente_logged_in'):
        return JsonResponse({'error': 'Debes iniciar sesión para vaciar el carrito.'}, status=403)

    usuario = request.user
    cliente = get_object_or_404(Cliente, usuario_ptr_id=usuario.id)
    carrito = get_object_or_404(Carrito, run=cliente, activo=True)

    carrito.activo = False
    carrito.save()

    return JsonResponse({'mensaje': 'Carrito vaciado.'}, status=200)