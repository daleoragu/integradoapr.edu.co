# notas/views/admin_crud_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.views.decorators.http import require_POST

from ..models import Estudiante, FichaEstudiante, Curso, AreaConocimiento, Materia
from ..forms import AdminCrearEstudianteForm, AdminEditarEstudianteForm, MateriaForm, AreaConocimientoForm

def es_admin(user):
    return user.is_superuser

# ===============================================================
# VISTAS PARA GESTIÓN DE ESTUDIANTES
# ===============================================================

@user_passes_test(es_admin)
def gestion_estudiantes_vista(request):
    cursos = Curso.objects.all()
    curso_seleccionado_id = request.GET.get('curso', '')
    query = request.GET.get('q', '')

    estudiantes_qs = Estudiante.objects.select_related('user', 'curso').all().order_by('user__last_name', 'user__first_name')

    if curso_seleccionado_id:
        estudiantes_qs = estudiantes_qs.filter(curso_id=curso_seleccionado_id)

    if query:
        estudiantes_qs = estudiantes_qs.filter(
            Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query)
        )

    context = {
        'estudiantes': estudiantes_qs,
        'cursos': cursos,
        'curso_seleccionado_id': curso_seleccionado_id,
        'search_query': query,
    }
    return render(request, 'notas/admin_crud/gestion_estudiantes.html', context)


@user_passes_test(es_admin)
@transaction.atomic
def crear_estudiante_vista(request):
    if request.method == 'POST':
        form = AdminCrearEstudianteForm(request.POST)
        if form.is_valid():
            nombres = form.cleaned_data['nombres']
            apellidos = form.cleaned_data['apellidos']
            tipo_documento = form.cleaned_data['tipo_documento']
            numero_documento = form.cleaned_data['numero_documento']
            curso = form.cleaned_data['curso']
            
            nuevo_usuario = User.objects.create_user(username=numero_documento, password=numero_documento, first_name=nombres, last_name=apellidos)
            
            try:
                grupo_estudiantes = Group.objects.get(name='Estudiantes')
                nuevo_usuario.groups.add(grupo_estudiantes)
            except Group.DoesNotExist:
                messages.error(request, "Error crítico: El grupo 'Estudiantes' no fue encontrado.")
                return redirect('crear_estudiante')

            nuevo_estudiante = Estudiante.objects.create(user=nuevo_usuario, curso=curso)
            FichaEstudiante.objects.create(estudiante=nuevo_estudiante, tipo_documento=tipo_documento, numero_documento=numero_documento)

            messages.success(request, f"¡Estudiante '{apellidos} {nombres}' creado con éxito! Ahora puedes completar los demás datos de su ficha.")
            return redirect('editar_estudiante', estudiante_id=nuevo_estudiante.id)
            
    else:
        form = AdminCrearEstudianteForm()

    context = { 'form': form, 'titulo': "Crear Nuevo Estudiante" }
    return render(request, 'notas/admin_crud/formulario_estudiante.html', context)


@user_passes_test(es_admin)
@transaction.atomic
def editar_estudiante_vista(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    ficha, created = FichaEstudiante.objects.get_or_create(estudiante=estudiante)

    if request.method == 'POST':
        form = AdminEditarEstudianteForm(request.POST, request.FILES, instance=ficha)
        if form.is_valid():
            form.save()
            messages.success(request, f"¡Estudiante '{ficha.estudiante.user.last_name} {ficha.estudiante.user.first_name}' actualizado con éxito!")
            return redirect('gestion_estudiantes')
    else:
        form = AdminEditarEstudianteForm(instance=ficha)

    context = { 'form': form, 'titulo': "Editar Estudiante", 'estudiante': estudiante }
    return render(request, 'notas/admin_crud/formulario_estudiante.html', context)


@user_passes_test(es_admin)
@require_POST
def eliminar_estudiante_vista(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    nombre_completo = f"{estudiante.user.last_name} {estudiante.user.first_name}"
    user_to_delete = estudiante.user
    
    user_to_delete.delete()
    
    messages.success(request, f"Estudiante '{nombre_completo}' ha sido eliminado permanentemente.")
    return redirect('gestion_estudiantes')


# ===============================================================
# VISTAS PARA GESTIÓN DE ÁREAS Y MATERIAS
# ===============================================================

@user_passes_test(es_admin)
def gestion_materias_vista(request):
    materias = Materia.objects.select_related('area').all().order_by('area__nombre', 'nombre')
    context = {'materias': materias}
    return render(request, 'notas/admin_crud/gestion_materias.html', context)

# --- VISTA QUE FALTABA ---
@user_passes_test(es_admin)
def gestion_areas_vista(request):
    """
    Muestra una lista de todas las áreas para su gestión (CRUD).
    """
    areas = AreaConocimiento.objects.all().order_by('nombre')
    context = {'areas': areas}
    return render(request, 'notas/admin_crud/gestion_areas.html', context)


# --- CRUD para Áreas ---
@user_passes_test(es_admin)
def crear_area_vista(request):
    if request.method == 'POST':
        form = AreaConocimientoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Área '{form.cleaned_data['nombre']}' creada con éxito.")
            return redirect('gestion_areas')
    else:
        form = AreaConocimientoForm()
    context = {'form': form, 'titulo': 'Crear Nueva Área de Conocimiento'}
    return render(request, 'notas/admin_crud/formulario_area.html', context)

@user_passes_test(es_admin)
def editar_area_vista(request, area_id):
    area = get_object_or_404(AreaConocimiento, id=area_id)
    if request.method == 'POST':
        form = AreaConocimientoForm(request.POST, instance=area)
        if form.is_valid():
            form.save()
            messages.success(request, f"Área '{area.nombre}' actualizada con éxito.")
            return redirect('gestion_areas')
    else:
        form = AreaConocimientoForm(instance=area)
    context = {'form': form, 'titulo': f"Editar Área: {area.nombre}"}
    return render(request, 'notas/admin_crud/formulario_area.html', context)

@user_passes_test(es_admin)
@require_POST
def eliminar_area_vista(request, area_id):
    area = get_object_or_404(AreaConocimiento, id=area_id)
    if area.materias.exists():
        messages.error(request, f"No se puede eliminar el área '{area.nombre}' porque contiene materias asociadas. Primero elimine o reasigne las materias.")
    else:
        nombre_area = area.nombre
        area.delete()
        messages.success(request, f"Área '{nombre_area}' eliminada con éxito.")
    return redirect('gestion_areas')


# --- CRUD para Materias ---
@user_passes_test(es_admin)
@transaction.atomic
def crear_materia_vista(request):
    if request.method == 'POST':
        form = MateriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Materia '{form.cleaned_data['nombre']}' creada con éxito.")
            return redirect('gestion_materias')
    else:
        form = MateriaForm()
    
    context = {'form': form, 'titulo': 'Añadir Nueva Materia'}
    return render(request, 'notas/admin_crud/formulario_materia.html', context)

@user_passes_test(es_admin)
@transaction.atomic
def editar_materia_vista(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    if request.method == 'POST':
        form = MateriaForm(request.POST, instance=materia)
        if form.is_valid():
            form.save()
            messages.success(request, f"Materia '{materia.nombre}' actualizada con éxito.")
            return redirect('gestion_materias')
    else:
        form = MateriaForm(instance=materia)

    context = {'form': form, 'titulo': f"Editar Materia: {materia.nombre}", 'materia': materia}
    return render(request, 'notas/admin_crud/formulario_materia.html', context)

@user_passes_test(es_admin)
@require_POST
def eliminar_materia_vista(request, materia_id):
    materia = get_object_or_404(Materia, id=materia_id)
    nombre_materia = materia.nombre
    try:
        materia.delete()
        messages.success(request, f"Materia '{nombre_materia}' eliminada con éxito.")
    except IntegrityError:
        messages.error(request, f"No se pudo eliminar la materia. Puede que esté asignada a un docente o tenga notas registradas.")
    
    return redirect('gestion_materias')
