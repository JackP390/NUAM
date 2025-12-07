from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.
class Cliente(models.Model):
    rut = models.CharField(max_length=12)
    nombre = models.CharField(max_length=250)
    direccion = models.CharField(max_length=150)
    email = models.EmailField(max_length=100)
    telefono = models.CharField(max_length=13)
    corredor = models.ForeignKey('Corredor', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id} - {self.nombre}'
    
class Emisor(models.Model):
    rut = models.CharField(max_length=12)
    nombre = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.id} - {self.nombre}'

# Esto maneja el hashing de manera automatica
class CustomCorredorManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # Esto se asegura que el email sea requerido y se normalice (por ejemplo que se ponga en minúsculas)
        if not email:
            raise ValueError('El email debe ser configurado')
        email = self.normalize_email(email)

        # Crea y guarda el corredor
        user = self.model(email=email, **extra_fields)
        user.set_password(password) # esto es para hashear la contraseña antes de guardarla
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True) # Maneja datos importantes del codigo de django
        extra_fields.setdefault('is_superuser', True) # Se puede hacer lo que sea con esté campo (por eso no lo tiene nadie)
        extra_fields.setdefault('is_active', True) # reemplaza el campo estado

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class Corredor(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email' #el campo que se usa en el login
    REQUIRED_FIELDS = ['nombre', 'rut', 'rol'] #campos que se piden al crear usuario

    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    rol = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False) # is_active es el campo estado, el AbstractBaseUser lo pide obligatoriamente con ese nombre
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=('groups'),
        blank=True,
        help_text=('Los grupos a los que pertenece este usuario. Un usuario tendra todos los permisos '
                   'otorgado para cada uno de los grupos.'
        ),
        related_name="corredor_set", # Si no se agrega este "apodo" el codigo colisiona
        related_query_name="corredor",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=('user_permissions'),
        blank=True,
        help_text=('Especifica permisos para esté usuario.',),
        related_name="corredor_permissions_set",
        related_query_name="corredor",
    )

    objects = CustomCorredorManager()

    def __str__(self):
        return f'{self.email}'
    
#calificación tributaria
class Calificacion(models.Model):
    id_cliente = models.ForeignKey('Cliente', on_delete=models.PROTECT) #si el cliente es eliminado la calificacion no se elimina
    id_emisor = models.ForeignKey('Emisor', on_delete=models.PROTECT) #lo mismo con el emisor 
    año_tributario = models.IntegerField(null=True)
    fecha_creacion_registro = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)
    #campos que estan en el E-R: [ID_Cliente, ID_Emisor]
    
    def __str__(self):
        return f'{self.id} - {self.año_tributario}'
    
#detalle calificacion
class Detalle_c(models.Model):
    id_calificacion = models.ForeignKey('Calificacion', on_delete=models.CASCADE) #si la calificación es eliminada se elimina su detalle
    id_corredor = models.ForeignKey('Corredor', on_delete=models.PROTECT) #a diferencia de si se "despide" el corredor
    tipo_dato = models.CharField(max_length=10)
    valor_monto = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    valor_factor = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    fecha_creacion_detalle = models.DateTimeField(auto_now_add=True)
    # campos que estan en el E-R: [ID_Calificacion, ID_Corredor, Emisor, fecha_creacion_registro]
    
    def __str__(self):
        return f'{self.id} - {self.tipo_dato}'