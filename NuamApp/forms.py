from django.forms import ModelForm
from .models import Cliente, Emisor, Corredor, Calificacion, Detalle_c

class FormCliente(ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'rut', 'direccion', 'email', 'telefono']

class FormEmisor(ModelForm):
    class Meta:
        model = Emisor
        fields = ['rut', 'nombre']

class FormCorredor(ModelForm):
    class Meta:
        model = Corredor
        fields = ['nombre', 'rut', 'email', 'contraseña']

class FormCalificacion(ModelForm):
    class Meta:
        model = Calificacion
        fields = ['año_tributario']

class FormDetalle_c(ModelForm):
    class Meta:
        model = Detalle_c
        fields = ['tipo_dato', 'valor_monto', 'valor_factor']


#si quieres ocupar todos los campos es '__all__'