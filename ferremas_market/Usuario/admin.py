from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Administrador, Cliente, Vendedor, Bodeguero, Contador
from .forms import AdministradorCreacionForm

class UsuarioAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'primer_nombre', 'primer_apellido', 'correo', 'is_active', 'run')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'primer_nombre', 'primer_apellido', 'correo', 'is_active'),
        }),
    )
    list_display = ('username', 'correo', 'primer_nombre', 'primer_apellido')

class AdministradorAdmin(UsuarioAdmin):
    form = AdministradorCreacionForm
    add_form = AdministradorCreacionForm
    model = Administrador
    fieldsets = (
        (None, {'fields': ('username', 'password', 'primer_nombre', 'primer_apellido', 'correo', 'run', 'contrasena_cambiada', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'primer_nombre', 'primer_apellido', 'correo', 'run', 'is_staff', 'is_superuser'),
        }),
    )
    list_display = ('username', 'correo', 'primer_nombre', 'primer_apellido')

# Usar UsuarioAdmin como base para otros roles
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Administrador, AdministradorAdmin)
admin.site.register(Cliente, UsuarioAdmin)
admin.site.register(Vendedor, UsuarioAdmin)
admin.site.register(Bodeguero, UsuarioAdmin)
admin.site.register(Contador, UsuarioAdmin)