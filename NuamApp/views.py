from django.shortcuts import render, redirect # redirect para enviar a otras páginas
from django.contrib.auth.decorators import login_required
from .models import Cliente, Emisor, Corredor, Calificacion, Detalle_c
from .forms import FormCliente, FormEmisor, FormCorredor, FormCalificacion, FormDetalle_c

# Create your views here.
def main(request):
    return render(request, 'main.html')

def register(request):
    if request.method == 'POST':
        form = FormCorredor(request.POST)
        if form.is_valid():
            password = form.cleaned_data.pop('password')
            form.cleaned_data.pop('password2')

            form.cleaned_data['rol'] = 'Corredor' # Se le asigna un valor por defecto

            Corredor.objects.create_user(
                password = password,
                **form.cleaned_data
            )
            return redirect('login')
    else:
            form = FormCorredor()
    return render(request, 'register.html', {'form':form})

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

            cliente.id_corredor = request.user

            cliente.save()

            return redirect('holder')
    else:
        form = FormCliente()

    context = {'form':form, 'titulo':'Añadir Nuevo Cliente', 'action_url':'create_client'}
    return render(request, 'create_client.html', context)