from django import forms
from django.forms import ModelForm, PasswordInput
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import Cliente, Emisor, Corredor, Calificacion, Detalle_c

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = get_user_model().EMAIL_FIELD

    username = forms.CharField(
        label="Correo Electrónico",
        widget=forms.TextInput(attrs={'class': 'campo', 'placeholder': 'Correo Electrónico'})
    )

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'campo', 'placeholder': 'Contraseña'})
    )

class FormCliente(ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'rut', 'direccion', 'email', 'telefono']

class FormEmisor(ModelForm):
    class Meta:
        model = Emisor
        fields = ['rut', 'nombre', 'estado']

class FormCorredor(ModelForm):
    class Meta:
        model = Corredor
        fields = ['nombre', 'rut', 'email', 'password']
        widgets = {'password':PasswordInput(),} # Oculta la contraseña al escribirla

class FormCalificacion(ModelForm):
    class Meta:
        model = Calificacion
        fields = ['año_tributario']

class FormDetalle_c(ModelForm):
    class Meta:
        model = Detalle_c
        fields = ['tipo_dato', 'valor_monto', 'valor_factor']


#si quieres ocupar todos los campos es '__all__'