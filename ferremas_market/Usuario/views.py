from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import Administrador


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
                if user is not None and user.is_staff == True:
                    login(request, user)
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

# def activar_cuenta(request, id):
#     administrador = Administrador.objects.get(id=id)
#     if request.method == 'POST':
#         form = SetPasswordForm(administrador, request.POST)
#         if form.is_valid():
#             administrador = form.save()
#             administrador.activado = True
#             administrador.is_staff = True
#             administrador.save()
#             return redirect('dashboard_administrador')
#     else:
#         form = SetPasswordForm(administrador)
#     return render(request, 'administrador/activar_cuenta.html', {'form': form})

def dashboard_administrador(request):
    return render(request, 'administrador/dashboard_administrador.html')