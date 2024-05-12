from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Administrador, Vendedor
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

class AdministradorCreacionForm(forms.ModelForm):
    class Meta:
        model = Administrador
        fields = ('primer_nombre', 'primer_apellido', 'correo', 'run', 'dv_run')

    def save(self, commit=True):
        administrador = super().save(commit=False)
        administrador.username = f"{self.cleaned_data['primer_nombre']}_{self.cleaned_data['primer_apellido']}"
        # Generar la contraseña
        password = (f"{self.cleaned_data['primer_nombre'][:3]}{self.cleaned_data['primer_apellido'][:3]}_{self.cleaned_data['run']}")
        administrador.password = password
        if commit:
            administrador.save()
            grupo = Group.objects.get_or_create(name='Administrador')
            administrador.groups.add(grupo)
            administrador.save()
        return administrador

# Formulario para cambiar contraseña de Administrador (Primer Ingreso)
class CambiarContrasenaAdministrador(forms.Form):
    password1 = forms.CharField(label='Nueva contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirma la nueva contraseña', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden")
        return cleaned_data

class VendedorCreacionForm(UserCreationForm):
    primer_nombre = forms.CharField(max_length=30, label='Primer Nombre')
    primer_apellido = forms.CharField(max_length=45, label='Primer Apellido')
    numero_telefonico = forms.CharField(max_length=12, required=False, label='Número Telefónico')
    correo = forms.EmailField(max_length=70, label='Correo')
    run = forms.IntegerField(label='Run')
    dv_run = forms.CharField(max_length=1, label='DV-Run')
    username = forms.CharField(max_length=20)

    class Meta:
        model = Vendedor
        fields = ('primer_nombre', 'primer_apellido', 'numero_telefonico', 'correo', 'run', 'dv_run', 'username', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.primer_nombre = self.cleaned_data["primer_nombre"]
        user.primer_apellido = self.cleaned_data["primer_apellido"]
        user.numero_telefonico = self.cleaned_data["numero_telefonico"]
        user.correo = self.cleaned_data["correo"]
        user.run = self.cleaned_data["run"]
        user.dv_run = self.cleaned_data["dv_run"]
        user.username = self.cleaned_data["username"]
        user.password = self.cleaned_data["password1"]
        if commit:
            user.save()
        return user