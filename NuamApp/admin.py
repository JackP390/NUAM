from django.contrib import admin
from .models import Cliente, Emisor, Corredor, Calificacion, Detalle_c

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Emisor)
admin.site.register(Corredor)
admin.site.register(Calificacion)
admin.site.register(Detalle_c)