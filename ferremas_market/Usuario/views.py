from django.http import Http404, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .models import Administrador, Vendedor, Cliente, Bodeguero, Contador
from django.shortcuts import render, get_object_or_404
from .forms import CambiarContrasenaAdministrador, VendedorCreacionForm, ClienteCreacionForm
from Pedidos.models import Producto
from functools import wraps
from django.core.paginator import Paginator
from .forms import CambiarContrasenaAdministrador

# Create your views here.

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
                user = Administrador.objects.get(username=username, password=password)
                if user.is_staff == True and user.is_active == True:
                    request.session['is_administrador_logged_in'] = True
                    print("Sesión establecida:", request.session['is_administrador_logged_in'])
                    if not user.contrasena_cambiada:
                        return redirect('activar_cuenta', id=user.id)
                    else:
                        return redirect('dashboard_administrador', id=user.id)
                else:
                    messages.error(request, 'Usuario no válido o no tienes permisos de administrador.')
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
            password1 = form.cleaned_data['password1']
            administrador.password = password1
            administrador.contrasena_cambiada = True
            administrador.save()
            return redirect('dashboard_administrador')
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


##################################
##            Cliente           ##
##################################

# Crear funcion de register y logueo

def index_cliente(request):
    productos = Producto.objects.all()
    context = {
        'productos': productos,
    }
    return render(request, 'cliente/index_cliente.html', context)

def logueo_cliente(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            try:
                user = Cliente.objects.get(username=username, password=password)
                if user.is_active == True:
                    request.session['is_cliente_logged_in'] = True
                    login(request, user)
                    return redirect('index_cliente')
                else:
                    messages.error(request, 'Usuario no válido, intentelo nuevamente.')
            except Vendedor.DoesNotExist:
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


##################################
##            Vendedor          ##
##################################

def logueo_vendedor(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            try:
                user = Vendedor.objects.get(username=username, password=password)
                if user.is_active == True:
                    request.session['is_vendedor_logged_in'] = True
                    login(request, user)
                    return redirect('index_vendedor')
                else:
                    messages.error(request, 'Usuario no válido, comuniquese con el administrador.')
            except Vendedor.DoesNotExist:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Debes ingresar tanto el nombre de usuario como la contraseña.')
        return render(request, 'vendedor/logueo_vendedor.html', {'form': None})
    else:
        return render(request, 'vendedor/logueo_vendedor.html', {'form': None})

@mantener_sesion('vendedor')
def index_vendedor(request):
    return render(request, 'vendedor/index_vendedor.html')