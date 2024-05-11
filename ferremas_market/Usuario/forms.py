from django import forms
from .models import Administrador
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

# Formulario para cambiar contraseña Adminsitrador
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