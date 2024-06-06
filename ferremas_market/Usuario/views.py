import bcrypt
from django.http import Http404, JsonResponse
from django.utils import timezone
from babel.dates import format_datetime
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse
from .models import Administrador, Vendedor, Cliente, Bodeguero, Contador
from django.shortcuts import render, get_object_or_404
from .forms import *
from django.db.models import Sum, Min, Max
from Pedidos.models import Categoria, Compra, DetalleCompra, Pedido, Producto
from functools import wraps
from django.core.paginator import Paginator
from .forms import CambiarContrasenaAdministrador

# Create your views here.

##################################
##    Formato Fecha Funciones   ##
##################################

def formatear_fecha(fecha):
    return format_datetime(fecha, "d 'de' MMMM y, h:mm a", locale='es')

##################################
##    Verificar tipo usuario    ##
##################################

# Decorador para mantener la sesion del actor y luego cerrarla
def mantener_sesion(tipo_usuario):
    def decorator(function):
        @wraps(function)
        def wrap(request, *args, **kwargs):
            session_key = f'is_{tipo_usuario}_logged_in'
            if request.session.get(session_key, False):
                return function(request, *args, **kwargs)
            else:
                return render(request, 'acceso_denegado.html')
        return wrap
    return decorator

def cerrar_sesion(tipo_usuario):
    def view(request):
        session_key = f'is_{tipo_usuario}_logged_in'
        request.session.pop(session_key, None)
        request.session.flush()
        if tipo_usuario == 'cliente':
            return redirect('index_cliente')
        return redirect(f'logueo_{tipo_usuario}')
    return view

# Crear funciones específicas usando la generalización para cerrar la sesion de los actores
cerrar_sesion_administrador = cerrar_sesion('administrador')
cerrar_sesion_vendedor = cerrar_sesion('vendedor')
cerrar_sesion_cliente = cerrar_sesion('cliente')
cerrar_sesion_bodeguero = cerrar_sesion('bodeguero')
cerrar_sesion_contador = cerrar_sesion('contador')


##################################
##         Administrador        ##
##################################

def logueo_administrador(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            try:
                user = Administrador.objects.get(username=username)
                if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                    if user.is_staff and user.is_active:
                        request.session['is_administrador_logged_in'] = True
                        if not user.contrasena_cambiada:
                            return redirect('activar_cuenta', id=user.id)
                        else:
                            return redirect('dashboard_administrador', id=user.id)
                    else:
                        messages.error(request, 'Usuario no válido o no tienes permisos de administrador.')
                else:
                    messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
            except Administrador.DoesNotExist:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Debes ingresar tanto el nombre de usuario como la contraseña.')
        return render(request, 'administrador/logueo_administrador.html', {'form': None})
    else:
        return render(request, 'administrador/logueo_administrador.html', {'form': None})

@mantener_sesion('administrador')
def activar_cuenta(request, id):
    administrador = get_object_or_404(Administrador, id=id)
    if request.method == 'POST':
        form = CambiarContrasenaAdministrador(request.POST)
        if form.is_valid():
            form.save(administrador)
            return redirect('dashboard_administrador', id=administrador.id)
    else:
        form = CambiarContrasenaAdministrador()
    return render(request, 'administrador/activar_cuenta.html', {'form': form})

@mantener_sesion('administrador')
def dashboard_administrador(request, id):
    administrador = Administrador.objects.get(id=id)
    request.session['administrador_id'] = administrador.id
    context = {'administrador': administrador}
    return render(request, 'administrador/dashboard_administrador.html', context)

# Metodos ADMINISTRADOR

# Creacion Usuarios

# Creacion de Vendedor
@mantener_sesion('administrador')
def crear_vendedor(request):
    administrador_id = request.session.get('administrador_id')
    try:
        administrador = Administrador.objects.get(id=administrador_id)
    except ObjectDoesNotExist:
        return redirect('logueo_administrador')
    if request.method == 'POST':
        form = VendedorCreacionForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            form.full_clean()
            return JsonResponse({'success': False, 'error': dict(form.errors)})
    else:
        form = VendedorCreacionForm()
    return render(request, 'administrador/vendedor/crear_vendedor.html', {'form': form, 'administrador': administrador})

@mantener_sesion('administrador')
def listar_vendedores(request):
    administrador_id = request.session.get('administrador_id')
    try:
        administrador = Administrador.objects.get(id=administrador_id)
    except ObjectDoesNotExist:
        return redirect('logueo_administrador')
    vendedor = Vendedor.objects.all()
    page = request.GET.get('page', 1)
    try:
        paginator = Paginator(vendedor, 5)
        vendedor = paginator.page(page)
    except:
        raise Http404
    context = {
        'entity': vendedor,
        'paginator': paginator,
        'administrador': administrador
    }
    return render(request, 'administrador/vendedor/listar_vendedores.html', context)

@mantener_sesion('administrador')
def modificar_vendedor(request, id):
    administrador_id = request.session.get('administrador_id')
    try:
        administrador = Administrador.objects.get(id=administrador_id)
    except ObjectDoesNotExist:
        return redirect('logueo_administrador')
    vendedor = get_object_or_404(Vendedor, id=id)
    if request.method == 'POST':
        form = VendedorCreacionForm(request.POST, instance=vendedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario vendedor modificado correctamente.')
            return redirect('listar_vendedores')
        else:
            messages.error(request, "No se ha podido modificar el usuario vendedor.")
    else:
        form = VendedorCreacionForm(instance=vendedor)
    context = {
        'form': form,
        'administrador': administrador
    }
    return render(request, 'administrador/vendedor/modificar_vendedor.html', context)

@mantener_sesion('administrador')
def eliminar_vendedor(request, id):
    administrador_id = request.session.get('administrador_id')
    try:
        administrador = Administrador.objects.get(id=administrador_id)
    except ObjectDoesNotExist:
        return redirect('logueo_administrador')
    vendedor = get_object_or_404(Vendedor, id=id)
    vendedor.delete()
    return redirect('listar_vendedores')

# Creacion de Bodeguero
@mantener_sesion('administrador')
def crear_bodeguero(request):
    administrador_id = request.session.get('administrador_id')
    try:
        administrador = Administrador.objects.get(id=administrador_id)
    except ObjectDoesNotExist:
        return redirect('logueo_administrador')
    if request.method == 'POST':
        form = BodegueroCreacionForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            form.full_clean()
            return JsonResponse({'success': False, 'error': dict(form.errors)})
    else:
        form = BodegueroCreacionForm()
    return render(request, 'administrador/bodeguero/crear_bodeguero.html', {'form': form, 'administrador': administrador})

@mantener_sesion('administrador')
def listar_bodegueros(request):
    administrador_id = request.session.get('administrador_id')
    try:
        administrador = Administrador.objects.get(id=administrador_id)
    except ObjectDoesNotExist:
        return redirect('logueo_administrador')
    bodeguero = Bodeguero.objects.all()
    page = request.GET.get('page', 1)
    try:
        paginator = Paginator(bodeguero, 5)
        bodeguero = paginator.page(page)
    except:
        raise Http404
    context = {
        'entity': bodeguero,
        'paginator': paginator,
        'administrador': administrador
    }
    return render(request, 'administrador/bodeguero/listar_bodegueros.html', context)

@mantener_sesion('administrador')
def modificar_bodeguero(request, id):
    administrador_id = request.session.get('administrador_id')
    try:
        administrador = Administrador.objects.get(id=administrador_id)
    except ObjectDoesNotExist:
        return redirect('logueo_administrador')
    bodeguero = get_object_or_404(Bodeguero, id=id)
    if request.method == 'POST':
        form = BodegueroCreacionForm(request.POST, instance=bodeguero)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario bodeguero modificado correctamente.')
            return redirect('listar_bodegueros')
        else:
            messages.error(request, "No se ha podido modificar el usuario bodeguero.")
    else:
        form = BodegueroCreacionForm(instance=bodeguero)
    context = {
        'form': form,
        'administrador': administrador
    }
    return render(request, 'administrador/bodeguero/modificar_bodeguero.html', context)

@mantener_sesion('administrador')
def eliminar_bodeguero(request, id):
    administrador_id = request.session.get('administrador_id')
    try:
        administrador = Administrador.objects.get(id=administrador_id)
    except ObjectDoesNotExist:
        return redirect('logueo_administrador')
    bodeguero = get_object_or_404(Bodeguero, id=id)
    bodeguero.delete()
    return redirect('listar_bodegueros')

# Creacion de Contador

@mantener_sesion('administrador')
def crear_contador(request):
    administrador_id = request.session.get('administrador_id')
    try:
        administrador = Administrador.objects.get(id=administrador_id)
    except ObjectDoesNotExist:
        return redirect('logueo_administrador')
    if request.method == 'POST':
        form = ContadorCreacionForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            form.full_clean()
            return JsonResponse({'success': False, 'error': dict(form.errors)})
    else:
        form = ContadorCreacionForm()
    return render(request, 'administrador/contador/crear_contador.html', {'form': form, 'administrador': administrador})

@mantener_sesion('administrador')
def listar_contadores(request):
    administrador_id = request.session.get('administrador_id')
    try:
        administrador = Administrador.objects.get(id=administrador_id)
    except ObjectDoesNotExist:
        return redirect('logueo_administrador')
    contador = Contador.objects.all()
    page = request.GET.get('page', 1)
    try:
        paginator = Paginator(contador, 5)
        contador = paginator.page(page)
    except:
        raise Http404
    context = {
        'entity': contador,
        'paginator': paginator,
        'administrador': administrador
    }
    return render(request, 'administrador/contador/listar_contadores.html', context)

@mantener_sesion('administrador')
def modificar_contador(request, id):
    administrador_id = request.session.get('administrador_id')
    try:
        administrador = Administrador.objects.get(id=administrador_id)
    except ObjectDoesNotExist:
        return redirect('logueo_administrador')
    contador = get_object_or_404(Contador, id=id)
    if request.method == 'POST':
        form = ContadorCreacionForm(request.POST, instance=contador)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario contador modificado correctamente.')
            return redirect('listar_contadores')
        else:
            messages.error(request, "No se ha podido modificar el usuario contador.")
    else:
        form = ContadorCreacionForm(instance=contador)
    context = {
        'form': form,
        'administrador': administrador
    }
    return render(request, 'administrador/contador/modificar_contador.html', context)

@mantener_sesion('administrador')
def eliminar_contador(request, id):
    administrador_id = request.session.get('administrador_id')
    try:
        administrador = Administrador.objects.get(id=administrador_id)
    except ObjectDoesNotExist:
        return redirect('logueo_administrador')
    contador = get_object_or_404(Contador, id=id)
    contador.delete()
    return redirect('listar_contadores')



##################################
##            Cliente           ##
##################################

# Crear funcion de register y logueo

def index_cliente(request):
    cliente_id = request.session.get('cliente_id')
    
    productos = Producto.objects.all()
    paginator = Paginator(productos, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'cliente_id': cliente_id,
    }
    return render(request, 'cliente/index_cliente.html', context)

def producto_individual(request, id):
    cliente_id = request.session.get('cliente_id')

    producto = get_object_or_404(Producto, id=id)
    productos = Producto.objects.exclude(id=id)
    context = {
        'producto': producto,
        'productos': productos,
        'cliente_id': cliente_id,
    }
    return render(request, 'cliente/producto_individual.html', context)

def carrito(request):
    cliente_id = request.session.get('cliente_id')

    print("Contenido del carrito en la sesión:", cliente_id)

    carrito = request.session.get('cart', [])

    print("Contenido del carrito en la sesión:", carrito)

    if carrito:
        productos_ids = [item['id'] for item in carrito]
        productos_carrito = Producto.objects.filter(id__in=productos_ids)
    else:
        productos_carrito = []

    context = {
        'productos_carrito': productos_carrito,
        'cliente_id': cliente_id,
    }

    return render(request, 'cliente/carrito.html', context)

def logueo_cliente(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            try:
                user = Cliente.objects.get(username=username)
                if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                    if user.is_active:
                        request.session['is_cliente_logged_in'] = True
                        request.session['cliente_id'] = user.id
                        return redirect('index_cliente')
                    else:
                        messages.error(request, 'Usuario no válido, intentelo nuevamente.')
                else:
                    messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
            except Cliente.DoesNotExist:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Debes ingresar tanto el nombre de usuario como la contraseña.')
        return render(request, 'cliente/logueo_cliente.html', {'form': None})
    else:
        return render(request, 'cliente/logueo_cliente.html', {'form': None})

def register_cliente(request):
    if request.method == 'POST':
        form = ClienteCreacionForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            form.full_clean()
            return JsonResponse({'success': False, 'error': dict(form.errors)})
    else:
        form = ClienteCreacionForm()
    return render(request, 'cliente/register_cliente.html', {'form': form})

@mantener_sesion('cliente')
def historial_compras(request):
    cliente_id = request.session.get('cliente_id')
    compras = Compra.objects.filter(usuario=cliente_id).order_by('-fecha_compra')

    estados_traducidos = {
        'INITIALIZED': 'Iniciado',
        'AUTHORIZED': 'Autorizado',
        'REVERSED': 'Revertido',
        'FAILED': 'Fallido',
        'NULLIFIED': 'Anulado',
        'PARTIALLY_NULLIFIED': 'Parcialmente anulado',
        'CAPTURED': 'Capturado',
        'Pendiente': 'Pendiente'
    }

    metodos_pago_traducidos = {
        'VD': 'Venta Débito',
        'VN': 'Venta Normal',
        'VC': 'Venta en cuotas',
        'SI': '3 cuotas sin interés',
        'S2': '2 cuotas sin interés',
        'NC': 'N Cuotas sin interés',
        'VP': 'Venta Prepago'
    }

    compras_traducidas = []
    for compra in compras:
        compra_traducida = compra
        compra_traducida.estado_traducido = estados_traducidos.get(compra.estado, compra.estado)
        compra_traducida.metodo_pago_traducido = metodos_pago_traducidos.get(compra.metodo_pago, compra.metodo_pago)
        compra_traducida.fecha_compra_formateada = formatear_fecha(compra.fecha_compra)
        compras_traducidas.append(compra_traducida)

    context = {
        'compras': compras_traducidas,
        'cliente_id': cliente_id,
    }
    return render(request, 'cliente/historial_compras.html', context)

def detalles_compra(request, compra_id):
    cliente_id = request.session.get('cliente_id')
    compra = Compra.objects.get(id=compra_id, usuario=cliente_id)
    detalles = DetalleCompra.objects.filter(compra=compra)

    estados_traducidos = {
        'INITIALIZED': 'Iniciado',
        'AUTHORIZED': 'Autorizado',
        'REVERSED': 'Revertido',
        'FAILED': 'Fallido',
        'NULLIFIED': 'Anulado',
        'PARTIALLY_NULLIFIED': 'Parcialmente anulado',
        'CAPTURED': 'Capturado',
        'Pendiente': 'Pendiente'
    }

    metodos_pago_traducidos = {
        'VD': 'Venta Débito',
        'VN': 'Venta Normal',
        'VC': 'Venta en cuotas',
        'SI': '3 cuotas sin interés',
        'S2': '2 cuotas sin interés',
        'NC': 'N Cuotas sin interés',
        'VP': 'Venta Prepago'
    }

    detalles_data = [
        {
            'producto_nombre': detalle.producto.nombre,
            'imagen': detalle.producto.foto.url,
            'cantidad': detalle.cantidad,
            'precio': detalle.precio
        }
        for detalle in detalles
    ]

    compra_data = {
        'id': compra.id,
        'fecha_compra': formatear_fecha(compra.fecha_compra),
        'total': compra.total,
        'metodo_pago': metodos_pago_traducidos.get(compra.metodo_pago, compra.metodo_pago),
        'numero_tarjeta': compra.numero_tarjeta,
        'codigo_autorizacion': compra.codigo_autorizacion,
        'estado': estados_traducidos.get(compra.estado, compra.estado),
        'detalles': detalles_data
    }
    return JsonResponse(compra_data)


##################################
##            Vendedor          ##
##################################

def logueo_vendedor(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            try:
                user = Vendedor.objects.get(username=username)
                if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                    if user.is_active:
                        request.session['is_vendedor_logged_in'] = True
                        login(request, user)
                        return redirect('index_vendedor')
                    else:
                        messages.error(request, 'Usuario no válido, comuniquese con el administrador.')
                else:
                    messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
            except Vendedor.DoesNotExist:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Debes ingresar tanto el nombre de usuario como la contraseña.')
        return render(request, 'vendedor/logueo_vendedor.html', {'form': None})
    else:
        return render(request, 'vendedor/logueo_vendedor.html', {'form': None})

@mantener_sesion('vendedor')
def index_vendedor(request):
    vendedor_id = request.session.get('vendedor_id')
    compras = Compra.objects.filter(estado='AUTHORIZED', decision_vendedor=False)
    pedidos_despacho = Pedido.objects.filter(estado=6)

    estados_traducidos = {
        'INITIALIZED': 'Iniciado',
        'AUTHORIZED': 'Autorizado',
        'REVERSED': 'Revertido',
        'FAILED': 'Fallido',
        'NULLIFIED': 'Anulado',
        'PARTIALLY_NULLIFIED': 'Parcialmente anulado',
        'CAPTURED': 'Capturado',
        'Pendiente': 'Pendiente'
    }

    producto_nombre = request.GET.get('producto_nombre', '')
    if producto_nombre:
        productos = Producto.objects.filter(nombre__icontains=producto_nombre)[:3]
    else:
        productos = []

    context = {
        'vendedor_id': vendedor_id,
        'compras': compras,
        'productos': productos,
        'estados_traducidos': estados_traducidos,
        'pedidos_despacho': pedidos_despacho
    }
    return render(request, 'vendedor/index_vendedor.html', context)

@mantener_sesion('vendedor')
def aprobar_pedido(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)
    cliente = compra.usuario

    pedido = Pedido.objects.create(
        run=cliente,
        estado=2,
        informacion_adicional=f'Pedido generado a partir de la compra {compra.id}',
        fecha_recivo=timezone.now(),
        fecha_envio=None,
        activo=True
    )
    pedido.save()

    compra.decision_vendedor = True
    compra.save()

    messages.success(request, 'Compra aprobada, enviando orden a bodeguero...')

    return redirect('index_vendedor')

@mantener_sesion('vendedor')
def rechazar_pedido(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)
    cliente = compra.usuario

    pedido = Pedido.objects.create(
        run=cliente,
        estado=5,
        informacion_adicional=f'Pedido generado a partir de la compra {compra.id}',
        fecha_recivo=timezone.now(),
        fecha_envio=None,
        activo=True
    )
    pedido.save()

    compra.decision_vendedor = True
    compra.save()

    messages.error(request, 'Compra rechazada, entregando mensaje al cliente...')

    return redirect('index_vendedor')

@mantener_sesion('vendedor')
def confirmar_despacho(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    pedido.estado = 7
    pedido.fecha_envio = timezone.now()
    pedido.save()

    messages.success(request, 'Pedido confirmado y en tránsito.')
    return redirect('index_vendedor')


##################################
##           Bodeguero          ##
##################################

def logueo_bodeguero(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            try:
                user = Bodeguero.objects.get(username=username)
                if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                    if user.is_active:
                        request.session['is_bodeguero_logged_in'] = True
                        request.session['bodeguero_id'] = user.id
                        login(request, user)
                        return redirect('index_bodeguero')
                    else:
                        messages.error(request, 'Usuario no válido, comuniquese con el administrador.')
                else:
                    messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
            except Bodeguero.DoesNotExist:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Debes ingresar tanto el nombre de usuario como la contraseña.')
        return render(request, 'bodeguero/logueo_bodeguero.html', {'form': None})
    else:
        return render(request, 'bodeguero/logueo_bodeguero.html', {'form': None})

@mantener_sesion('bodeguero')
def index_bodeguero(request):
    bodeguero_id = request.session.get('bodeguero_id')
    categorias = Categoria.objects.all()

    categoria_id = request.GET.get('categoria')
    producto_id = request.GET.get('producto')
    productos = Producto.objects.filter(categoria_id=categoria_id) if categoria_id else Producto.objects.all()
    producto_seleccionado = Producto.objects.get(id=producto_id) if producto_id else None

    if request.method == "POST":
        pedido_id = request.POST.get('pedido_id')
        action = request.POST.get('action')

        if pedido_id and action:
            pedido = get_object_or_404(Pedido, id=pedido_id)
            if action == 'confirmar' and pedido.estado == 1:
                pedido.estado = 2
                pedido.save()
                messages.success(request, 'Preparando pedido')
                print("Pedido confirmado:", pedido)
            elif action == 'entregar' and pedido.estado == 2:
                pedido.estado = 3
                pedido.save()
                print("Pedido entregado:", pedido)

    pedidos = Pedido.objects.all()
    print("Pedidos obtenidos:", pedidos)

    context = {
        'categorias': categorias,
        'productos': productos,
        'bodeguero_id': bodeguero_id,
        'categoria_seleccionada': int(categoria_id) if categoria_id else None,
        'producto_seleccionado': producto_seleccionado,
        'pedidos': pedidos,
    }
    return render(request, 'bodeguero/index_bodeguero.html', context)

@mantener_sesion('bodeguero')
def actualizar_stock(request, producto_id):
    producto = Producto.objects.get(id=producto_id)
    accion = request.POST.get('accion')

    if accion == 'incrementar':
        producto.stock += 1
    elif accion == 'disminuir' and producto.stock > 0:
        producto.stock -= 1

    producto.save()
    return redirect('index_bodeguero')

def listar_pedidos(request):
    pedidos = Pedido.objects.all()
    print("Pedidos obtenidos:", pedidos)
    return render(request, 'pedidos/listar_pedidos.html', {'pedidos': pedidos})

def confirmar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    print("Pedido a confirmar:", pedido)
    if pedido.estado == 1:
        pedido.estado = 2
        pedido.save()
        messages.success(request, 'Preparando pedido')
        print("Pedido confirmado:", pedido)
    return redirect('listar_pedidos')

def entregar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    print("Pedido a entregar:", pedido)
    if pedido.estado == 2:
        pedido.estado = 3
        pedido.save()
        print("Pedido entregado:", pedido)
    return redirect('listar_pedidos')


##################################
##           Contador           ##
##################################

def logueo_contador(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            try:
                user = Contador.objects.get(username=username)
                if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                    if user.is_active:
                        request.session['is_contador_logged_in'] = True
                        login(request, user)
                        return redirect('index_contador')
                    else:
                        messages.error(request, 'Usuario no válido, comuniquese con el administrador.')
                else:
                    messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
            except Contador.DoesNotExist:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Debes ingresar tanto el nombre de usuario como la contraseña.')
        return render(request, 'contador/logueo_contador.html', {'form': None})
    else:
        return render(request, 'contador/logueo_contador.html', {'form': None})

@mantener_sesion('contador')
def index_contador(request):
    compras = Compra.objects.all()
    return render(request, 'contador/index_contador.html', {'compras': compras})

def confirmar_pago(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)
    return redirect('index_contador')

def rechazar_pago(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id)
    return redirect('index_contador')

def registrar_entrega(request):
    if request.method == 'POST':
        numero_orden = request.POST.get('numero-orden')
        cliente = request.POST.get('cliente')
        fecha_entrega = request.POST.get('fecha-entrega')
        return redirect('index_contador')
    return render(request, 'contador/index_contador.html')





#############################################################
##            Filtros Pagina Cliente (Productos)           ##
#############################################################

def productos_todos(request):
    productos = Producto.objects.filter(activo=True)
    paginator = Paginator(productos, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'cliente/index_cliente.html', context)

def productos_mas_vendidos(request):
    detalles = DetalleCompra.objects.values('producto').annotate(total_vendido=Sum('cantidad')).order_by('-total_vendido')[:16]
    productos_ids = [detalle['producto'] for detalle in detalles]
    productos = Producto.objects.filter(id__in=productos_ids, activo=True)
    paginator = Paginator(productos, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'cliente/index_cliente.html', context)

def productos_nuevos(request):
    productos = Producto.objects.filter(activo=True).order_by('-id')[:16]
    paginator = Paginator(productos, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'cliente/index_cliente.html', context)

def catalogo_productos(request):
    cliente_id = request.session.get('cliente_id')
    productos = Producto.objects.all()

    categoria_id = request.GET.get('categoria')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    activo = request.GET.get('activo')

    # Asegurarse de que los valores 'None' no causen problemas
    if categoria_id and categoria_id != 'None' and categoria_id != '':
        try:
            categoria_id = int(categoria_id)
            productos = productos.filter(categoria_id=categoria_id)
        except ValueError:
            categoria_id = None

    if precio_min and precio_min != 'None' and precio_min != '':
        try:
            precio_min = float(precio_min)
        except ValueError:
            precio_min = None

    if precio_max and precio_max != 'None' and precio_max != '':
        try:
            precio_max = float(precio_max)
        except ValueError:
            precio_max = None

    if precio_min is not None and precio_max is not None:
        productos = productos.filter(precio__gte=precio_min, precio__lte=precio_max)

    if activo and activo != 'None' and activo.lower() == 'true':
        productos = productos.filter(activo=True)

    precios = productos.aggregate(Min('precio'), Max('precio'))
    precio_min_valor = precios['precio__min'] if precios['precio__min'] is not None else 0
    precio_max_valor = precios['precio__max'] if precios['precio__max'] is not None else 0

    paginator = Paginator(productos, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categorias = Categoria.objects.filter(activo=True)

    context = {
        'page_obj': page_obj,
        'categorias': categorias,
        'cliente_id': cliente_id,
        'precio_min_valor': precio_min_valor,
        'precio_max_valor': precio_max_valor,
        'categoria_id': categoria_id,
        'precio_min': precio_min,
        'precio_max': precio_max,
        'activo': activo,
    }
    return render(request, 'cliente/catalogo_productos.html', context)