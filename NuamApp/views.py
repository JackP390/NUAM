from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
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

@login_required
def redireccion_login(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.rol == 'Cliente':
        return redirect('client_view')
    else:
        return redirect('holder')
    
def csrf_failure(request, reason=""):
    context = {'titulo': 'Sesión Expirada'}
    return render(request, '403_csrf.html', context)

@user_passes_test(es_admin)
def carga_masiva_calificaciones(request):
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
    clientes = Cliente.objects.all().select_related('corredor').order_by('nombre')

    context = {
        'corredores':corredores,
        'emisores':emisores,
        'clientes':clientes,
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
            # 1. Guardar Cliente (Ficha de datos)
            cliente = form.save(commit=False)
            cliente.corredor = request.user
            cliente.save()

            # 2. Crear Usuario y Enviar Correo
            rut_limpio = cliente.rut
            try:
                # Verificamos si ya existe el usuario
                if not Corredor.objects.filter(rut=rut_limpio).exists():
                    # Generar contraseña aleatoria
                    password_provisoria = get_random_string(length=8)
                    
                    # Crear el usuario para loguearse
                    Corredor.objects.create_user(
                        email=cliente.email,
                        nombre=cliente.nombre,
                        rut=rut_limpio,
                        password=password_provisoria,
                        rol='Cliente',
                        is_active=True
                    )

                    # --- PREPARAR EL CORREO ---
                    asunto = 'Bienvenido a NUAM - Credenciales de Acceso'
                    mensaje = f"""
                    Hola {cliente.nombre},

                    Tu corredor {request.user.nombre} te ha registrado en la plataforma NUAM.
                    
                    Tus credenciales de acceso son:
                    --------------------------------
                    Usuario (Email): {cliente.email}
                    Contraseña: {password_provisoria}
                    --------------------------------

                    Por favor ingresa en: http://127.0.0.1:8000/login/
                    """
                    
                    # --- ENVIAR EL CORREO ---
                    try:
                        send_mail(
                            asunto,
                            mensaje,
                            settings.EMAIL_HOST_USER,
                            [cliente.email],
                            fail_silently=False,
                        )
                        print("\n" + "="*30)
                        print(f"CORREO ENVIADO A CONSOLA PARA: {cliente.email}")
                        print("="*30 + "\n")
                        messages.success(request, f"Cliente creado y correo enviado a {cliente.email}")
                    except Exception as e:
                        messages.warning(request, f"Cliente creado, pero falló el envío: {e}")
                        messages.info(request, f"Clave generada: {password_provisoria}")

                else:
                    messages.warning(request, "El cliente se creó, pero ya tenía un usuario registrado.")

            except Exception as e:
                messages.error(request, f"Error en el proceso de usuario: {e}")

            return redirect('holder')
    else:
        form = FormCliente()

    context = {
        'form': form,
        'titulo': 'Añadir Nuevo Cliente',
        'action': reverse('create_client')
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

@login_required
def client_detail(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id, corredor=request.user)

    calificaciones = Calificacion.objects.filter(id_cliente=cliente).order_by('-año_tributario')

    form = FormCalificacion()

    context = {
        'cliente':cliente,
        'calificaciones':calificaciones,
        'form':form
    }
    
    return render(request, 'client_detail.html', context)

@login_required
def add_calificacion(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id, corredor= request.user)

    if request.method == 'POST':
        form = FormCalificacion(request.POST)
        if form.is_valid():
            nueva_calif = form.save(commit=False)
            nueva_calif.id_cliente = cliente
            nueva_calif.save()
            messages.success(request, "Calificación asociada correctamente.")
        else:
            messages.error(request, "Error al asociar calificación.")

    return redirect('client_detail', cliente_id=cliente_id)

@login_required
def client_view(request):
    if request.user.rol != 'Cliente':
        return redirect('redireccion_login')
    
    try:
        ficha_cliente = Cliente.objects.filter(rut=request.user.rut).first()

        if ficha_cliente:
            calificaciones = Calificacion.objects.filter(id_cliente=ficha_cliente).order_by('-año_tributario')
        else:
            calificaciones = []
            messages.warning(request, "No se encontró tu ficha de cliente.")

    except Exception as e:
        ficha_cliente = None
        calificaciones = []
        messages.error(request, f"Error al cargar datos: {e}")

    context = {
        'cliente':ficha_cliente,
        'calificaciones':calificaciones
    }

    return render(request, 'client_view.html', context)