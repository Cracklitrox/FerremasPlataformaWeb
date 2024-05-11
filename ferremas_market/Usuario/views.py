from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .models import Administrador
from django.shortcuts import render, get_object_or_404
from .forms import CambiarContrasenaAdministrador
from Pedidos.models import Producto


# Create your views here.

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
                if user.is_staff == True:
                    login(request, user)
                    if not user.contrasena_cambiada:
                        return redirect('activar_cuenta', id=user.id)
                    else:
                        return redirect('dashboard_administrador')
                else:
                    messages.error(request, 'Usuario no válido o no tienes permisos de administrador.')
            except Administrador.DoesNotExist:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Debes ingresar tanto el nombre de usuario como la contraseña.')
        return render(request, 'administrador/logueo_administrador.html', {'form': None})
    else:
        return render(request, 'administrador/logueo_administrador.html', {'form': None})

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

def dashboard_administrador(request):
    return render(request, 'administrador/dashboard_administrador.html')


##################################
##            Cliente           ##
##################################

def index_cliente(request):
    productos = Producto.objects.all()
    context = {
        'productos': productos,
    }
    return render(request, 'cliente/index_cliente.html', context)