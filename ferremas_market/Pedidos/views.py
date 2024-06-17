import uuid
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.error.transbank_error import TransbankError
from django.shortcuts import render, redirect
from django.conf import settings
import json
from .models import *
from Usuario.models import Cliente

def obtener_o_crear_carrito(usuario):
    carrito, created = Carrito.objects.get_or_create(usuario=usuario)
    return carrito

def manejar_compra(cliente_id, carrito, transaction_id):
    try:
        cliente = Cliente.objects.get(id=cliente_id)
    except Cliente.DoesNotExist:
        print(f"Cliente con id {cliente_id} no encontrado")
        return None, 'Cliente no encontrado'

    if Compra.objects.filter(transaction_id=transaction_id).exists():
        return None, 'Compra ya procesada'

    compra = Compra.objects.create(usuario=cliente, total=0, transaction_id=transaction_id)
    total_compra = 0

    for item in carrito:
        try:
            producto = Producto.objects.get(id=item.producto.id)
        except Producto.DoesNotExist:
            print(f"Producto con id {item.producto.id} no encontrado")
            return None, f'Producto con id {item.producto.id} no encontrado'

        precio_total_item = producto.precio * item.cantidad
        total_compra += precio_total_item
        
        DetalleCompra.objects.create(
            compra=compra,
            producto=producto,
            cantidad=item.cantidad,
            precio=producto.precio
        )

    compra.total = total_compra
    compra.save()
    return compra, None

def iniciar_transaccion(request):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=401)
    
    cliente = Cliente.objects.get(id=cliente_id)
    carrito = obtener_o_crear_carrito(cliente)
    transaction_id = uuid.uuid4()
    compra, error = manejar_compra(cliente_id, carrito.items.all(), transaction_id)
    if error:
        return JsonResponse({'success': False, 'error': error}, status=400)

    transaction = Transaction(settings.TRANSBANK_COMMERCE_CODE, settings.TRANSBANK_API_KEY, settings.TRANSBANK_ENVIRONMENT)
    response = transaction.create(
        buy_order=str(compra.id),
        session_id=str(cliente_id),
        amount=compra.total,
        return_url=request.build_absolute_uri(reverse('confirmar_transaccion'))
    )
    
    return JsonResponse({'success': True, 'redirect_url': response['url'] + '?token_ws=' + response['token']})

@csrf_exempt
def actualizar_stock(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            usuario_id = data.get('usuario_id')
            items = data.get('items', [])

            print(f"Usuario ID recibido: {usuario_id}")
            print(f"Items recibidos: {items}")

            if not usuario_id:
                return JsonResponse({'success': False, 'error': 'Usuario no especificado'}, status=400)

            cliente = Cliente.objects.get(id=usuario_id)
            carrito = obtener_o_crear_carrito(cliente)
            carrito.items.all().delete()

            for item in items:
                producto = Producto.objects.get(id=item['id'])
                ItemCarrito.objects.create(carrito=carrito, producto=producto, cantidad=item['quantity'])

            transaction_id = uuid.uuid4()
            compra, error = manejar_compra(usuario_id, carrito.items.all(), transaction_id)
            if error:
                print(f"Error en manejar_compra: {error}")
                return JsonResponse({'success': False, 'error': error}, status=400)

            print(f"Compra guardada: {compra}")

            try:
                transaction = Transaction().configure_for_testing()
                response = transaction.create(
                    buy_order=str(compra.id),
                    session_id=str(usuario_id),
                    amount=compra.total,
                    return_url=request.build_absolute_uri(reverse('confirmar-transaccion'))
                )

                request.session['cliente_id'] = usuario_id

                return JsonResponse({'success': True, 'redirect_url': response['url'] + '?token_ws=' + response['token']})

            except TransbankError as e:
                print(f"Error en la creación de la transacción: {str(e)}")
                compra.delete()
                return JsonResponse({'success': False, 'error': 'Error en la creación de la transacción'}, status=500)

        except json.JSONDecodeError as e:
            print(f"Error de decodificación JSON: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Error de decodificación JSON: {str(e)}'}, status=400)
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Error inesperado: {str(e)}'}, status=500)
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

def confirmar_transaccion(request):
    token = request.GET.get('token_ws')
    if not token:
        tbk_token = request.GET.get('TBK_TOKEN')
        tbk_order = request.GET.get('TBK_ORDEN_COMPRA')
        
        if tbk_token:
            compra = Compra.objects.get(id=tbk_order)
            if compra.estado != 'Anulada':
                compra.estado = 'NULLIFIED'
                compra.save()
            
            return render(request, 'compra_anulada.html', {'compra': compra})

        return redirect('/Usuario/')

    transaction = Transaction().configure_for_testing()
    try:
        response = transaction.commit(token)
    except TransbankError as e:
        tbk_order = request.GET.get('TBK_ORDEN_COMPRA')
        compra = Compra.objects.get(id=tbk_order)
        if compra.estado != 'Anulada':
            compra.estado = 'NULLIFIED'
            compra.save()
        
        return render(request, 'compra_anulada.html', {'compra': compra})

    print("Respuesta de Transbank:", response)

    if response['status'] == 'AUTHORIZED':
        compra_id = int(response['buy_order'])
        compra = Compra.objects.get(id=compra_id)
        compra.total = response['amount']
        compra.metodo_pago = response['payment_type_code']
        
        card_detail = response['card_detail']
        compra.numero_tarjeta = card_detail['card_number'][-4:]
        compra.codigo_autorizacion = response['authorization_code']
        compra.codigo_respuesta = str(response['response_code'])
        compra.estado = response['status']
        compra.numero_cuotas = response.get('installments_number', 0)
        
        if compra.numero_cuotas > 0:
            compra.monto_cuota = round(compra.total / compra.numero_cuotas)
        else:
            compra.monto_cuota = 0
        
        compra.fecha_autorizacion = response['accounting_date']
        compra.fechaHora_autorizacion = response['transaction_date']
        compra.saldo_transaccion = response.get('balance', 0)

        compra.save()

        detalles = DetalleCompra.objects.filter(compra=compra)
        for detalle in detalles:
            producto = detalle.producto
            producto.stock -= detalle.cantidad
            producto.save()

        TarjetaCredito.objects.create(
            usuario=compra.usuario,
            numero_tarjeta=compra.numero_tarjeta,
            tipo_tarjeta=compra.metodo_pago,
            alias=f'Tarjeta {compra.metodo_pago} {compra.numero_tarjeta[-4:]}',
            activa=True
        )
        
        response = render(request, 'compra_exitosa.html', {'response': response, 'limpiar_carrito': True})
        return response
    else:
        compra_id = int(response['buy_order'])
        compra = Compra.objects.get(id=compra_id)
        compra.estado = 'FAILED'
        compra.save()
        return render(request, 'compra_fallida.html', {'response': response, 'limpiar_carrito': False})

def anular_compra(request):
    token = request.GET.get('token_ws')
    transaction = Transaction().configure_for_testing()
    
    try:
        response = transaction.status(token)
        if response['status'] in ['INITIALIZED', 'AUTHORIZED']:
            response = transaction.refund(token, response['amount'])
            if response['status'] == 'REVERSED':
                compra_id = int(response['buy_order'])
                compra = Compra.objects.get(id=compra_id)
                compra.estado = 'Anulada'
                compra.save()
                
                return JsonResponse({'success': True, 'message': 'Compra anulada y stock restaurado'})
        return JsonResponse({'success': False, 'message': 'No se pudo anular la compra'})
    except TransbankError as e:
        print(f"Error al anular la compra: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Error al anular la compra'})

@csrf_exempt
def anadir_al_carrito(request, product_id):
    if request.method == 'POST':
        usuario = Cliente.objects.get(id=request.session.get('cliente_id'))
        producto = Producto.objects.get(id=product_id)
        carrito = obtener_o_crear_carrito(usuario)
        
        item_carrito, created = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
        if not created:
            item_carrito.cantidad += 1
        item_carrito.save()
        
        return JsonResponse({'success': True, 'message': 'Producto agregado al carrito'})

def obtener_carrito(request):
    usuario = Cliente.objects.get(id=request.session.get('cliente_id'))
    carrito = obtener_o_crear_carrito(usuario)
    items = carrito.items.all()
    cart_data = [{'producto_id': item.producto.id, 'nombre': item.producto.nombre, 'cantidad': item.cantidad, 'precio': item.producto.precio, 'imagen': item.producto.foto.url} for item in items]
    
    return JsonResponse({'cart': cart_data})

@csrf_exempt
def guardar_carrito(request):
    if request.method == 'POST':
        usuario = Cliente.objects.get(id=request.session.get('cliente_id'))
        data = json.loads(request.body)
        carrito = obtener_o_crear_carrito(usuario)
        carrito.items.all().delete()
        
        for item in data['items']:
            producto = Producto.objects.get(id=item['id'])
            ItemCarrito.objects.create(carrito=carrito, producto=producto, cantidad=item['quantity'])
        
        return JsonResponse({'success': True, 'message': 'Carrito guardado correctamente'})
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)