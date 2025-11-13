from django.db import models
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError #para los errores de validacion
import re #expresiones regulares (para depurar la contraseña)

SPECIAL_CHARS = r'[!@#$%^&*()_\-+=|\\/?\.,:;`~<>]'

# Create your models here.
class Cliente(models.Model):
    id_cliente = models.CharField(max_length=15, primary_key=True, editable=False)
    rut = models.CharField(max_length=12)
    nombre = models.CharField(max_length=250)
    direccion = models.CharField(max_length=150)
    email = models.EmailField(max_length=100)
    telefono = models.CharField(max_length=13)

    def save(self, *args,**kwargs):
        if not self.id_cliente:
            last_client = Cliente.objects.all().order_by('id_cliente').last()

            new_id_number = 1

            if last_client:
                last_id_str = last_client.id_cliente[1:]

                try:
                    last_id_number = int(last_id_str)
                    new_id_number = last_id_number + 1
                except ValueError:
                    return ('Error con el valor ID')
                
            self.id_cliente = f'U{new_id_number}'

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.id_cliente} - {self.nombre}'
    
class Emisor(models.Model):
    id_emisor = models.CharField(max_length=15, primary_key=True, editable=False)
    rut = models.CharField(max_length=12)
    nombre = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.id_emisor:
            last_issuer = Emisor.objects.all().order_by('id_emisor').last()

            new_id_number = 1

            if last_issuer:
                last_id_str = last_issuer.id_emisor[1:]

                try:
                    last_id_number = int(last_id_str)
                    new_id_number = last_id_number + 1
                except ValueError:
                    return ('Error con el valor ID')
                
            self.id_emisor = f'E{new_id_number}'

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.id_emisor} - {self.nombre}'

class Corredor(models.Model):
    id_corredor = models.CharField(max_length=15, primary_key=True, editable=False)
    rut = models.CharField(max_length=12)
    email = models.EmailField(max_length=100)
    contraseña = models.CharField(max_length=128)
    rol = models.CharField(max_length=50)
    estado = models.BooleanField(default=False)

    def clean(self): #para realizar la validacion
        super().clean() #llama al metodo clean padre/raiz/principal

        password = self.contraseña
        if len(password) < 128: #con esto solo se valida si es texto no si es un cifrado
            if len(password) < 8: #La contraseña debe tener minimo 8 caracteres como dice abajo
                raise ValidationError({'contraseña': "La contraseña debe tener al menos 8 caracteres."})
                #se llama al validation error con el nombre del campo para que se muestre el error más claro

            if not re.search(r'[A-Z]', password): #La contraseña debe tener una letra mayuscula... como dice abajo
                raise ValidationError({'contraseña': "La contraseña debe contener al menos una letra mayúscula."})
            
            if not re.search(SPECIAL_CHARS, password): #un caracter especial, como dice abajo
                raise ValidationError({'contraseña': f"La contraseña debe contener al menos un caracter especial: {SPECIAL_CHARS}"})


    def save(self, *args, **kwargs):
        #maneja la encriptación de la contraseña
        if len(self.contraseña) < 128:
            self.contraseña = make_password(self.contraseña)

        if not self.id_corredor:
            #ultimo corredor de bolsa
            last_stockbroker = Corredor.objects.all().order_by('id_corredor').last()

            new_id_number = 1

            if last_stockbroker:
                last_id_str = last_stockbroker.id_corredor[1:]

                try:
                    last_id_number = int(last_id_str)
                    new_id_number = last_id_number + 1
                except ValueError:
                    return ('Error con el valor ID')
                
            self.id_corredor = f'E{new_id_number}'

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.id_corredor} - {self.nombre}'
    
#calificación tributaria
class Calificacion(models.Model):
    id_calificacion = models.CharField(max_length=15, primary_key=True, editable=False)
    año_tributario = models.IntegerField(null=True)
    fecha_creacion_registro = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id_calificacion:
            last_qualification = Calificacion.objects.all().order_by('id_calificacion').last()

            new_id_number = 1

            if last_qualification:
                last_id_str = last_qualification.id_calificacion[1:]

                try:
                    last_id_number = int(last_id_str)
                    new_id_number = last_id_number + 1
                except ValueError:
                    return ('Error con el valor ID')
                
            self.id_calificacion = f'E{new_id_number}'

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.id_calificacion} - {self.nombre}'
    
