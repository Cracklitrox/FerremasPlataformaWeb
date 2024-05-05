from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import make_password
from .models import Administrador

class AdministradorCreacionForm(UserCreationForm):
    class Meta:
        model = Administrador
        fields = ('username', 'primer_nombre', 'primer_apellido', 'correo', 'run')

    def save(self, commit=True):
        user = super().save(commit=False)
        # Contraseña personalizada
        password = make_password(f'{user.primer_nombre}_{user.run}')
        user.set_password(password)
        user.contrasena_cambiada = False  # Asume que debe cambiarla al iniciar sesión
        user.is_staff = True  # Permitir acceso al panel administrativo
        user.is_superuser = False  # No tiene todos los permisos automáticamente
        if commit:
            user.save()
        return user