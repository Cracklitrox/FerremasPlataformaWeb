from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Producto, Compra, DetalleCompra
from Usuario.models import Cliente

@csrf_exempt
def actualizar_stock(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            usuario_id = data.get('usuario_id')
            print(f"Usuario ID recibido: {usuario_id}")
            if not usuario_id:
                return JsonResponse({'success': False, 'error': 'Usuario no especificado'}, status=400)
            try:
                cliente = Cliente.objects.get(id=usuario_id)
                print(f"Cliente encontrado: {cliente}")
            except Cliente.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Cliente no encontrado'}, status=404)
            
            compra = Compra.objects.create(usuario=cliente, total=0)
            total_compra = 0

            for item in data.get('items', []):
                try:
                    producto = Producto.objects.get(id=item['id'])
                    print(f"Producto encontrado: {producto}")
                except Producto.DoesNotExist:
                    return JsonResponse({'success': False, 'error': f'Producto con id {item["id"]} no encontrado'}, status=404)

                if producto.stock >= item['quantity']:
                    producto.stock -= item['quantity']
                    producto.save()
                    
                    precio_total_item = producto.precio * item['quantity']
                    total_compra += precio_total_item
                    
                    DetalleCompra.objects.create(
                        compra=compra,
                        producto=producto,
                        cantidad=item['quantity'],
                        precio=producto.precio
                    )
                else:
                    return JsonResponse({'success': False, 'error': f'Stock insuficiente para {producto.nombre}'}, status=400)
            
            compra.total = total_compra
            compra.save()
            print(f"Compra guardada: {compra}")
            return JsonResponse({'success': True})
        except Exception as e:
            print(f"Error inesperado: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Error inesperado: {str(e)}'}, status=500)
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)