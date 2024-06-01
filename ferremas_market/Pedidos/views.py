import uuid
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.error.transbank_error import TransbankError
from django.shortcuts import render, redirect
from django.conf import settings
import json
from .models import Producto, Compra, DetalleCompra, TarjetaCredito
from Usuario.models import Cliente


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
            producto = Producto.objects.get(id=item['id'])
        except Producto.DoesNotExist:
            print(f"Producto con id {item['id']} no encontrado")
            return None, f'Producto con id {item["id"]} no encontrado'

        precio_total_item = producto.precio * item['quantity']
        total_compra += precio_total_item
        
        DetalleCompra.objects.create(
            compra=compra,
            producto=producto,
            cantidad=item['quantity'],
            precio=producto.precio
        )

    compra.total = total_compra
    compra.save()
    return compra, None

def iniciar_transaccion(request):
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=401)
    
    carrito = request.session.get('carrito', [])
    transaction_id = uuid.uuid4()  # Generar un ID único para la transacción
    compra, error = manejar_compra(cliente_id, carrito, transaction_id)
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
            carrito = data.get('items', [])

            print(f"Usuario ID recibido: {usuario_id}")
            print(f"Carrito recibido: {carrito}")

            if not usuario_id:
                return JsonResponse({'success': False, 'error': 'Usuario no especificado'}, status=400)

            transaction_id = uuid.uuid4()
            
            compra, error = manejar_compra(usuario_id, carrito, transaction_id)
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
                request.session['carrito'] = carrito

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
        # Manejo de anulación de la transacción
        tbk_token = request.GET.get('TBK_TOKEN')
        tbk_order = request.GET.get('TBK_ORDEN_COMPRA')
        tbk_session = request.GET.get('TBK_ID_SESION')
        
        if tbk_token:
            # Aquí puedes manejar la anulación de la compra
            compra = Compra.objects.get(id=tbk_order)
            if compra.estado != 'Anulada':
                compra.estado = 'Anulada'
                compra.save()
            
            return render(request, 'compra_anulada.html', {'compra': compra})
        
        # Si no hay TBK_TOKEN, redirige o maneja el error adecuadamente
        return redirect('/Usuario/')  # O cualquier página de error que desees mostrar

    transaction = Transaction().configure_for_testing()
    try:
        response = transaction.commit(token)
    except TransbankError as e:
        # Si hay un error con Transbank, maneja la anulación de la compra
        tbk_order = request.GET.get('TBK_ORDEN_COMPRA')
        compra = Compra.objects.get(id=tbk_order)
        if compra.estado != 'Anulada':
            compra.estado = 'Anulada'
            compra.save()
        
        return render(request, 'compra_anulada.html', {'compra': compra})

    print("Respuesta de Transbank:", response)  # Para depuración

    if response['status'] == 'AUTHORIZED':
        compra_id = int(response['buy_order'])
        compra = Compra.objects.get(id=compra_id)
        compra.total = response['amount']
        compra.metodo_pago = response['payment_type_code']
        
        # Extraer los detalles de la tarjeta de 'card_detail'
        card_detail = response['card_detail']
        compra.numero_tarjeta = card_detail['card_number'][-4:]
        compra.codigo_autorizacion = response['authorization_code']
        compra.codigo_respuesta = str(response['response_code'])
        compra.estado = response['status']
        compra.numero_cuotas = response.get('installments_number')
        compra.monto_cuota = response.get('installments_amount', 0)
        compra.fecha_autorizacion = response['accounting_date']
        compra.fechaHora_autorizacion = response['transaction_date']
        compra.saldo_transaccion = response.get('balance', 0)

        compra.save()

        # Reducir el stock después de que la transacción sea autorizada
        detalles = DetalleCompra.objects.filter(compra=compra)
        for detalle in detalles:
            producto = detalle.producto
            producto.stock -= detalle.cantidad
            producto.save()

        # Guardar la tarjeta de crédito
        TarjetaCredito.objects.create(
            usuario=compra.usuario,
            numero_tarjeta=compra.numero_tarjeta,
            tipo_tarjeta=compra.metodo_pago,
            alias=f'Tarjeta {compra.metodo_pago} {compra.numero_tarjeta[-4:]}',
            activa=True
        )
        
        # Renderizar la página de compra exitosa e incluir la bandera para limpiar el carrito
        return render(request, 'compra_exitosa.html', {'response': response, 'limpiar_carrito': True})
    else:
        compra_id = int(response['buy_order'])
        compra = Compra.objects.get(id=compra_id)
        compra.estado = 'Fallida'
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