from django.shortcuts import render, redirect, get_object_or_404 # redirect para enviar a otras páginas y get object para obtener objetos
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from .models import Cliente, Emisor, Corredor, Calificacion, Detalle_c
from .forms import FormCliente, FormEmisor, FormCorredor, FormCalificacion, FormDetalle_c
import csv
import io

# Create your views here.
def main(request):
    return render(request, 'main.html')

def register(request):
    if request.method == 'POST':
        form = FormCorredor(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            nombre = form.cleaned_data.get('nombre')
            rut = form.cleaned_data.get('rut')
            password = form.cleaned_data.get('password')

            try:
                Corredor.objects.create_user(
                    email=email,
                    nombre=nombre,
                    rut=rut,
                    password=password,
                    rol = 'Corredor'
                )
            except Exception as e:
                form.add_error(None, f'Error al crear usuario: {e}')
                return render(request, 'register.html', {'form':form})

            return redirect('login')
    else:
            form = FormCorredor()
    return render(request, 'register.html', {'form':form})

def es_admin(user): # verificación de que el usuario es superuser/admin 
    return user.is_superuser

@login_required

@user_passes_test(es_admin)
def carga_masiva_clasificaciones(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo_csv')

        if not archivo:
            messages.error(request, "Debes subir un archivo.")
            return redirect('admin_dashboard')

        if not archivo.name.endswith('.csv'):
            messages.error(request, "El archivo debe ser CSV.")
            return redirect('admin_dashboard')
        
        try:
            data_set = archivo.read().decode('UTF-8')
            io_string = io.StringIO(data_set)
            next(io_string)

            for column in csv.reader(io_string, delimiter=',', quotechar='|'):
                rut_cliente = column[0]
                rut_emisor = column[1]
                anio = column[2]

                try:
                    cliente_obj = Cliente.objects.get(rut=rut_cliente)
                    emisor_obj = Emisor.objects.get(rut=rut_emisor)

                    Calificacion.objects.create(
                        id_cliente=cliente_obj,
                        id_emisor=emisor_obj,
                        año_tributario=anio
                    )
                except Cliente.DoesNotExist:
                    messages.warning(request, f"Cliente con RUT {rut_cliente} no encontrado. Saltando línea.")
                    continue
                except Emisor.DoesNotExist:
                    messages.warning(request, f"Emisor con rut {rut_emisor} no encontrado. Saltando línea.")
                    continue

            messages.success(request, "Proceso de carga masiva finalizado.")
        except Exception as e:
            messages.error(request, f"Error crítico procesando archivo: {e}")
    
    return redirect('admin_dashboard')

@user_passes_test(es_admin, login_url='login')
def admin_dashboard(request):
    corredores = Corredor.objects.all().order_by('id')
    emisores = Emisor.objects.all().order_by('nombre')

    context = {
        'corredores':corredores,
        'emisores':emisores,
        'form_emisor':FormEmisor()
    }
    return render(request, 'admin_dashboard.html', context)

@user_passes_test(es_admin)
def toggle_status_corredor(request, user_id):
    corredor = get_object_or_404(Corredor, pk=user_id)

    if corredor == request.user:
        messages.error(request, "No puedes desactivar tu propia cuenta.")
    else:
        corredor.is_active = not corredor.is_active
        corredor.save()
        estado = "activado" if corredor.is_active else "desactivado"
        messages.success(request, f"Usuario {corredor.nombre} {estado}.")

    return redirect('admin_dashboard')

@user_passes_test(es_admin)
def create_emisor(request):
    if request.method == 'POST':
        form = FormEmisor(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Emisor creado correctamente.")
        else:
            messages.error(request, "Error al crear emisor. Verifique los datos.")
    return redirect('admin_dashboard')

@user_passes_test(es_admin)
def delete_any_client(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    cliente.delete()
    messages.success(request, "Cliente eliminado del sistema.")
    return redirect('admin_dashboard')

@login_required # Hace que solo los corredores logeados puedan entrar a la página
def holder(request):
    corredor_actual = request.user # si el corredor esta en el request user

    clientes_asociados = Cliente.objects.filter(corredor=corredor_actual).order_by('nombre')
    context = {
        'nombre_e':corredor_actual.nombre, # nombre empleado logeado
        'clientes':clientes_asociados,
        }
    return render(request, 'holder.html', context)

@login_required
def create_client(request):
    if request.method == 'POST':
        form = FormCliente(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False) # Guarda el objeto cliente temporalmente

            cliente.corredor = request.user

            cliente.save()

            return redirect('holder')
    else:
        form = FormCliente()

    context = {
        'form':form,
        'titulo':'Añadir Nuevo Cliente',
        'action':reverse('create_client')
        }
    return render(request, 'form_client.html', context)

@login_required
def modify_client(request, cliente_id):
    try:
        cliente = Cliente.objects.get(pk=cliente_id, corredor = request.user)
    except Cliente.DoesNotExist:
        return render(request, '404.html', status=404)
    
    if request.method == 'POST':
        form = FormCliente(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('holder')
        
    else:
        form = FormCliente(instance=cliente)

    context = {
        'form':form,
        'titulo':'Modificar Cliente',
        'action':reverse('modify_client', kwargs={'cliente_id':cliente_id})
    }
    
    return render(request, 'form_client.html', context)

@require_POST
@login_required
def delete_client(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id, corredor=request.user) # se asegura que el cliente sea del corredor logeado

    cliente.delete()

    return redirect('holder')