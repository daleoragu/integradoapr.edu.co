# notas/views/admin_crud_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Q, Sum
from django.views.decorators.http import require_POST

from ..models import (
    Estudiante, FichaEstudiante, Curso, AreaConocimiento, Materia, Docente, 
    AsignacionDocente, FichaDocente
)
# Se importan TODOS los formularios desde su ubicación correcta
from ..forms import (
    AdminCrearEstudianteForm, AdminEditarEstudianteForm, MateriaForm, 
    AreaConocimientoForm, CursoForm, AdminCrearDocenteForm, AdminEditarDocenteForm,
    AsignacionDocenteForm
)

def es_personal_admin(user):
    """Verifica si el usuario es superusuario o pertenece al grupo 'Administradores'."""
    return user.is_superuser or user.groups.filter(name='Administradores').exists()

# ===============================================================
# VISTA PRINCIPAL DE ASIGNACIÓN ACADÉMICA
# ===============================================================
@user_passes_test(es_personal_admin)
def gestion_asignacion_academica_vista(request):
    docentes_list = Docente.objects.select_related('user').prefetch_related(
        'asignaciondocente_set__materia',
        'asignaciondocente_set__curso',
        'cursos_dirigidos'
    ).annotate(
        total_ih=Sum('asignaciondocente__intensidad_horaria_semanal', default=0)
    ).order_by('user__last_name')
    cursos_list = Curso.objects.annotate(
        total_ih=Sum('asignaciondocente__intensidad_horaria_semanal', default=0)
    ).order_by('nombre')
    form_asignacion = AsignacionDocenteForm()
    context = {
        'docentes_list': docentes_list,
        'cursos_list': cursos_list,
        'form_asignacion': form_asignacion,
        'titulo': "Panel de Asignación Académica"
    }
    return render(request, 'notas/admin_crud/gestion_asignacion_academica.html', context)

@user_passes_test(es_personal_admin)
@require_POST
def crear_asignacion_vista(request):
    form = AsignacionDocenteForm(request.POST)
    if form.is_valid():
        try:
            form.save()
            messages.success(request, 'Asignación creada correctamente.')
        except IntegrityError:
            messages.error(request, 'Error: Esta asignación ya existe.')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"Error en el campo '{form.fields[field].label}': {error}")
    return redirect('gestion_asignacion_academica')

@user_passes_test(es_personal_admin)
@require_POST
def eliminar_asignacion_vista(request, asignacion_id):
    asignacion = get_object_or_404(AsignacionDocente, id=asignacion_id)
    asignacion.delete()
    messages.success(request, 'Asignación eliminada correctamente.')
    return redirect('gestion_asignacion_academica')


# ===============================================================
# VISTAS PARA GESTIÓN DE DOCENTES (Lógica Completa)
# ===============================================================
@user_passes_test(es_personal_admin)
def gestion_docentes_vista(request):
    docentes = Docente.objects.select_related('user').all().order_by('user__last_name')
    context = {'docentes': docentes}
    return render(request, 'notas/admin_crud/gestion_docentes.html', context)

@user_passes_test(es_personal_admin)
@transaction.atomic
def crear_docente_vista(request):
    if request.method == 'POST':
        form = AdminCrearDocenteForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            nuevo_usuario = User.objects.create_user(
                username=datos['numero_documento'],
                password=datos['numero_documento'],
                first_name=datos['nombres'],
                last_name=datos['apellidos'],
                email=datos['email']
            )
            try:
                grupo_docentes, _ = Group.objects.get_or_create(name='Docentes')
                nuevo_usuario.groups.add(grupo_docentes)
            except Group.DoesNotExist:
                messages.warning(request, "El grupo 'Docentes' no existe.")
            
            nuevo_docente = Docente.objects.create(user=nuevo_usuario)
            FichaDocente.objects.create(docente=nuevo_docente)
            messages.success(request, f"¡Docente '{datos['apellidos']} {datos['nombres']}' creado con éxito!")
            return redirect('editar_docente', docente_id=nuevo_docente.id)
    else:
        form = AdminCrearDocenteForm()
    context = {'form': form, 'titulo': "Crear Nuevo Docente"}
    return render(request, 'notas/admin_crud/formulario_docente.html', context)

@user_passes_test(es_personal_admin)
@transaction.atomic
def editar_docente_vista(request, docente_id):
    docente = get_object_or_404(Docente, id=docente_id)
    ficha, created = FichaDocente.objects.get_or_create(docente=docente)
    if request.method == 'POST':
        form = AdminEditarDocenteForm(request.POST, instance=ficha, docente=docente)
        if form.is_valid():
            form.save()
            messages.success(request, f"¡Docente '{docente.user.get_full_name()}' actualizado con éxito!")
            return redirect('gestion_docentes')
    else:
        form = AdminEditarDocenteForm(instance=ficha, docente=docente)
    context = {'form': form, 'titulo': "Editar Ficha del Docente", 'docente': docente}
    return render(request, 'notas/admin_crud/formulario_docente.html', context)

@user_passes_test(es_personal_admin)
@require_POST
def eliminar_docente_vista(request, docente_id):
    docente = get_object_or_404(Docente, id=docente_id)
    docente.user.delete()
    messages.success(request, f"Docente '{docente.user.get_full_name()}' eliminado permanentemente.")
    return redirect('gestion_docentes')

# ===============================================================
# VISTAS PARA GESTIÓN DE CURSOS / GRADOS
# ===============================================================

@user_passes_test(es_personal_admin)
def gestion_cursos_vista(request):
    cursos = Curso.objects.select_related('director_grado__user').all()
    context = {'cursos': cursos}
    return render(request, 'notas/admin_crud/gestion_cursos.html', context)

@user_passes_test(es_personal_admin)
def crear_curso_vista(request):
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Curso creado exitosamente!')
            return redirect('gestion_cursos')
    else:
        form = CursoForm()
    context = {'form': form, 'titulo': 'Crear Nuevo Curso / Grado'}
    return render(request, 'notas/admin_crud/formulario_generico.html', context)

@user_passes_test(es_personal_admin)
def editar_curso_vista(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Curso actualizado exitosamente!')
            return redirect('gestion_cursos')
    else:
        form = CursoForm(instance=curso)
    context = {'form': form, 'titulo': f'Editar Curso: {curso.nombre}'}
    return render(request, 'notas/admin_crud/formulario_generico.html', context)

@user_passes_test(es_personal_admin)
@require_POST
def eliminar_curso_vista(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if curso.estudiante_set.exists():
        messages.error(request, f"No se puede eliminar '{curso.nombre}' porque tiene estudiantes asignados.")
    else:
        nombre_curso = curso.nombre
        curso.delete()
        messages.success(request, f"Curso '{nombre_curso}' eliminado con éxito.")
    return redirect('gestion_cursos')
    
# ===============================================================
# VISTAS PARA GESTIÓN DE ESTUDIANTES (CÓDIGO ORIGINAL INTEGRADO)
# ===============================================================

@user_passes_test(es_personal_admin)
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


@user_passes_test(es_personal_admin)
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
                grupo_estudiantes, _ = Group.objects.get_or_create(name='Estudiantes')
                nuevo_usuario.groups.add(grupo_estudiantes)
            except Group.DoesNotExist:
                messages.error(request, "Error crítico: El grupo 'Estudiantes' no fue encontrado.")
                return redirect('crear_estudiante')
            nuevo_estudiante = Estudiante.objects.create(user=nuevo_usuario, curso=curso)
            FichaEstudiante.objects.create(estudiante=nuevo_estudiante, tipo_documento=tipo_documento, numero_documento=numero_documento)
            messages.success(request, f"¡Estudiante '{apellidos} {nombres}' creado con éxito!")
            return redirect('editar_estudiante', estudiante_id=nuevo_estudiante.id)
    else:
        form = AdminCrearEstudianteForm()
    context = { 'form': form, 'titulo': "Crear Nuevo Estudiante" }
    return render(request, 'notas/admin_crud/formulario_estudiante.html', context)


@user_passes_test(es_personal_admin)
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


@user_passes_test(es_personal_admin)
@require_POST
def eliminar_estudiante_vista(request, estudiante_id):
    estudiante = get_object_or_404(Estudiante, id=estudiante_id)
    estudiante.user.delete()
    messages.success(request, f"Estudiante '{estudiante.user.get_full_name()}' ha sido eliminado permanentemente.")
    return redirect('gestion_estudiantes')


# ===============================================================
# VISTAS PARA GESTIÓN DE ÁREAS Y MATERIAS (CÓDIGO ORIGINAL INTEGRADO)
# ===============================================================

@user_passes_test(es_personal_admin)
def gestion_materias_vista(request):
    materias = Materia.objects.select_related('area').all().order_by('area__nombre', 'nombre')
    context = {'materias': materias}
    return render(request, 'notas/admin_crud/gestion_materias.html', context)

@user_passes_test(es_personal_admin)
def gestion_areas_vista(request):
    areas = AreaConocimiento.objects.all().order_by('nombre')
    context = {'areas': areas}
    return render(request, 'notas/admin_crud/gestion_areas.html', context)


@user_passes_test(es_personal_admin)
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
    return render(request, 'notas/admin_crud/formulario_generico.html', context)

@user_passes_test(es_personal_admin)
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
    return render(request, 'notas/admin_crud/formulario_generico.html', context)

@user_passes_test(es_personal_admin)
@require_POST
def eliminar_area_vista(request, area_id):
    area = get_object_or_404(AreaConocimiento, id=area_id)
    if area.materias.exists():
        messages.error(request, f"No se puede eliminar el área '{area.nombre}' porque contiene materias asociadas.")
    else:
        nombre_area = area.nombre
        area.delete()
        messages.success(request, f"Área '{nombre_area}' eliminada con éxito.")
    return redirect('gestion_areas')


@user_passes_test(es_personal_admin)
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

@user_passes_test(es_personal_admin)
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

@user_passes_test(es_personal_admin)
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
