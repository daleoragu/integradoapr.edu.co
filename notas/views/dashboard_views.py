# notas/views/dashboard_views.py
# Se ha corregido la vista del panel de administración para que sea más segura
# y pase la información correcta a la plantilla.

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from ..models import Estudiante, Docente
from django.http import HttpResponseNotFound

def es_admin_o_superusuario(user):
    """
    Verifica si el usuario es superusuario o pertenece al grupo de administradores del colegio.
    Asegúrate de tener un grupo llamado 'AdminColegio'.
    """
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name='AdminColegio').exists()

@login_required
def dashboard_vista(request):
    """
    Redirige a los usuarios al panel correspondiente según su rol.
    """
    if not request.colegio:
        return HttpResponseNotFound("<h1>Colegio no configurado para este dominio.</h1>")

    if not request.user.is_authenticated:
        return redirect('logout')
    
    if es_admin_o_superusuario(request.user):
        return redirect('admin_dashboard')
    
    if Docente.objects.filter(user=request.user, colegio=request.colegio).exists():
        return redirect('panel_docente')

    if Estudiante.objects.filter(user=request.user, colegio=request.colegio).exists():
        return redirect('panel_estudiante') 

    return render(request, 'notas/dashboard.html', {'colegio': request.colegio})


@login_required
@user_passes_test(es_admin_o_superusuario)
def admin_dashboard_vista(request):
    """
    Muestra el panel de administración principal.
    Ahora verifica si el admin también es docente y pasa esa información a la plantilla.
    """
    if not request.colegio:
        return HttpResponseNotFound("<h1>Colegio no configurado.</h1>")
    
    # Verificamos si el usuario administrador también tiene un perfil de docente en este colegio.
    user_is_also_docente = Docente.objects.filter(user=request.user, colegio=request.colegio).exists()
    
    context = {
        'colegio': request.colegio,
        'user_is_also_docente': user_is_also_docente # Pasamos la bandera a la plantilla
    }
    return render(request, 'notas/admin_tools/admin_dashboard.html', context)


@login_required
def docente_dashboard_vista(request):
    """
    Muestra el panel principal para el docente.
    """
    if not request.colegio:
        return HttpResponseNotFound("<h1>Colegio no configurado.</h1>")

    if not (request.user.is_superuser or Docente.objects.filter(user=request.user, colegio=request.colegio).exists()):
        return redirect('dashboard')

    context = {
        'colegio': request.colegio
    }
    return render(request, 'notas/docente/dashboard_docente.html', context)


@login_required
def estudiante_dashboard_vista(request):
    """
    Muestra el panel principal para el estudiante.
    """
    if not request.colegio:
        return HttpResponseNotFound("<h1>Colegio no configurado.</h1>")
        
    try:
        estudiante = Estudiante.objects.get(user=request.user, colegio=request.colegio)
        context = {
            'estudiante': estudiante,
            'colegio': request.colegio
        }
    except Estudiante.DoesNotExist:
        context = {
            'estudiante': None,
            'colegio': request.colegio
        }
        
    return render(request, 'notas/estudiante/panel_estudiante.html', context)
