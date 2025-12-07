from django import forms
from django.forms import ModelForm, PasswordInput, TextInput, CheckboxInput
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError #para los errores de validacion
from .models import Cliente, Emisor, Corredor, Calificacion, Detalle_c
import re # Expresiones regulares, para depurar la contraseña

SPECIAL_CHARS = r'[!@#$%^&*()_\-+=|\\/?\.,:;`~<>]'

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = get_user_model().USERNAME_FIELD

    username = forms.CharField(
        label="Correo Electrónico",
        widget=forms.TextInput(attrs={'class': 'campo', 'placeholder': 'Correo Electrónico', 'required': 'required'})
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'campo', 'placeholder': 'Contraseña', 'required': 'required'})
    )

class FormCliente(ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'rut', 'direccion', 'email', 'telefono']

class FormEmisor(ModelForm):
    class Meta:
        model = Emisor  
        fields = ['rut', 'nombre', 'estado']
        widgets = {
            'rut': TextInput(attrs={'class':'campo', 'placeholder':'RUT del Emisor'}),
            'nombre': TextInput(attrs={'class':'campo', 'placeholder':'Razón Social'}),# nombre oficial y legal de la empresa
        }

class FormEmisor(ModelForm):
    class Meta:
        model = Emisor
        fields = ['rut', 'nombre', 'estado']

class FormCorredor(ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'campo', 'placeholder': 'Contraseña'}),
        help_text="Mínimo 8 caracteres, 1 mayúscula y un caracter especial."
    )

    password2 = forms.CharField(
        label="Repetir Contraseña",
        widget= forms.PasswordInput(attrs={'class':'campo', 'placeholder':'Repetir Contraseña'}),
        help_text="Repita la contraseña para confirmar."
    )
    class Meta:
        model = Corredor
        fields = ['nombre', 'rut', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            self.add_error('password2', "Las contraseñas no coinciden.")

        if password:
            if len(password) < 8:
                self.add_error('password', "La contraseña debe tener al menos 8 caracteres.")

            if not re.search(r'[A-Z]', password):
                self.add_error('password', "La contraseña debe contener al menos una letra mayúscula.")

            if not re.search(SPECIAL_CHARS, password):
                self.add_error('password', f"La contraseña debe contener al menos un caracter especial: {SPECIAL_CHARS}")

        return cleaned_data

class FormCalificacion(ModelForm):
    class Meta:
        model = Calificacion
        fields = ['año_tributario']

class FormDetalle_c(ModelForm):
    class Meta:
        model = Detalle_c
        fields = ['tipo_dato', 'valor_monto', 'valor_factor']


#si quieres ocupar todos los campos es '__all__'