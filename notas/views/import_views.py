# notas/views/import_views.py
import csv
import io
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.db import transaction, IntegrityError

try:
    from openpyxl import load_workbook
    EXCEL_SUPPORT = True
except ImportError:
    EXCEL_SUPPORT = False

from ..models.perfiles import Estudiante, Docente, Curso, FichaEstudiante
from ..models.academicos import Materia, AreaConocimiento

def es_superusuario(user):
    return user.is_superuser

@login_required
@user_passes_test(es_superusuario)
def importacion_vista(request):
    """
    Handles the upload and processing of files for bulk data loading.
    Supports .xlsx for students and subjects, and .csv for teachers.
    """
    if request.method == 'POST' and 'archivo_importacion' in request.FILES:
        tipo_importacion = request.POST.get('tipo_importacion')
        archivo = request.FILES['archivo_importacion']

        try:
            with transaction.atomic():
                if tipo_importacion == 'estudiantes':
                    if not EXCEL_SUPPORT:
                        raise Exception("The 'openpyxl' library is required to import students from Excel. Please install it with 'pip install openpyxl'.")
                    if not archivo.name.endswith('.xlsx'):
                        raise Exception("To import students, please select a valid Excel file (.xlsx).")
                    _procesar_excel_estudiantes(request, archivo)
                
                elif tipo_importacion == 'materias':
                    if not EXCEL_SUPPORT:
                        raise Exception("The 'openpyxl' library is required to import subjects. Please install it with 'pip install openpyxl'.")
                    if not archivo.name.endswith('.xlsx'):
                         raise Exception(f"To import subjects, please select a valid Excel file (.xlsx).")
                    _procesar_excel_materias(request, archivo)

                elif tipo_importacion == 'docentes':
                    if not archivo.name.endswith('.csv'):
                        raise Exception(f"To import teachers, please select a valid CSV file.")
                    
                    try:
                        data_set = archivo.read().decode('utf-8')
                    except UnicodeDecodeError:
                        data_set = archivo.read().decode('latin-1')
                    
                    io_string = io.StringIO(data_set)
                    next(io_string)  # Skip header
                    reader = csv.reader(io_string, delimiter=';')
                    _procesar_csv_docentes(request, reader)
                else:
                    raise Exception("The selected import type is not valid.")

        except IntegrityError as e:
            messages.error(request, f"Integrity error: A data item (like a document) may already exist. Details: {e}")
        except Exception as e:
            messages.error(request, f"Error during the process: {e}")

        # Redirects to the page from which the request was made
        return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

    return redirect('admin_dashboard')

def _procesar_excel_estudiantes(request, archivo):
    """Logic to process the student Excel file."""
    creados, errores = 0, 0
    grupo_estudiantes, _ = Group.objects.get_or_create(name="Estudiantes")
    
    wb = load_workbook(archivo, data_only=True)
    sheet = wb.active
    map_tipo_doc = {v: k for k, v in FichaEstudiante.TIPO_DOCUMENTO_CHOICES}
    map_tipo_doc_keys = {k: v for k, v in FichaEstudiante.TIPO_DOCUMENTO_CHOICES}
    map_grupo_sang = {v: k for k, v in FichaEstudiante.GRUPO_SANGUINEO_CHOICES}

    for i, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), 2):
        try:
            if not any(row): continue
            (nombres, apellidos, tipo_doc_str, num_doc, nombre_curso, fecha_nac_str, 
             lugar_nac, eps, grupo_sang_str, enfermedades, nombre_padre, cel_padre,
             nombre_madre, cel_madre, nombre_acud, cel_acud, email_acud, 
             espera_porteria_str, colegio_ant, grado_ant) = row[:20]
            if not num_doc:
                raise ValueError("The document number is mandatory.")
            num_doc = str(num_doc).strip()
            if User.objects.filter(username=num_doc).exists():
                continue
            curso = Curso.objects.filter(nombre=str(nombre_curso).strip().upper()).first()
            if not curso:
                raise ValueError(f"The course '{nombre_curso}' does not exist.")
            user = User.objects.create_user(username=num_doc, password=num_doc, first_name=str(nombres or '').strip().upper(), last_name=str(apellidos or '').strip().upper())
            user.groups.add(grupo_estudiantes)
            estudiante_obj = Estudiante.objects.create(user=user, curso=curso)
            fecha_nacimiento = None
            if isinstance(fecha_nac_str, datetime):
                fecha_nacimiento = fecha_nac_str.date()
            elif isinstance(fecha_nac_str, str):
                try:
                    fecha_nacimiento = datetime.strptime(fecha_nac_str, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    fecha_nacimiento = None
            FichaEstudiante.objects.create(
                estudiante=estudiante_obj,
                tipo_documento=map_tipo_doc.get(str(tipo_doc_str).strip(), map_tipo_doc_keys.get(str(tipo_doc_str).strip(), 'OT')),
                numero_documento=num_doc,
                fecha_nacimiento=fecha_nacimiento,
                lugar_nacimiento=lugar_nac,
                eps=eps,
                grupo_sanguineo=map_grupo_sang.get(str(grupo_sang_str).strip(), None),
                enfermedades_alergias=enfermedades,
                nombre_padre=nombre_padre,
                celular_padre=cel_padre,
                nombre_madre=nombre_madre,
                celular_madre=cel_madre,
                nombre_acudiente=nombre_acud,
                celular_acudiente=cel_acud,
                email_acudiente=email_acud,
                espera_en_porteria=True if espera_porteria_str and 'SI' in str(espera_porteria_str).upper() else False,
                colegio_anterior=colegio_ant,
                grado_anterior=grado_ant
            )
            creados += 1
        except Exception as e:
            messages.warning(request, f"Error in student Excel row {i}: {e}")
            errores += 1
    messages.success(request, f"Student process completed. Created: {creados}. Errors/Skipped: {errores}.")

def _procesar_excel_materias(request, archivo):
    """Logic to process the subject Excel file."""
    creadas, errores = 0, 0
    wb = load_workbook(archivo, data_only=True)
    sheet = wb.active
    for i, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), 2):
        try:
            if not any(row): continue
            nombre_materia, abreviatura, ih_str, nombre_area = row[:4]
            nombre_materia = str(nombre_materia).strip().upper()
            if not nombre_materia or not nombre_area: continue
            if Materia.objects.filter(nombre=nombre_materia).exists(): continue
            
            area, _ = AreaConocimiento.objects.get_or_create(nombre=str(nombre_area).strip().upper())
            
            intensidad_horaria = None
            if ih_str and str(ih_str).isdigit():
                intensidad_horaria = int(ih_str)

            Materia.objects.create(
                nombre=nombre_materia, 
                area=area,
                abreviatura=str(abreviatura).strip().upper() if abreviatura else None,
                intensidad_horaria=intensidad_horaria
            )
            creadas += 1
        except Exception as e:
            messages.warning(request, f"Error in subject Excel row {i}: {e}")
            errores += 1
    messages.success(request, f"Subject process completed. Created: {creadas}. Errors/Skipped: {errores}.")

def _procesar_csv_docentes(request, reader):
    """Logic to process the teacher CSV (preserved)."""
    creados, errores = 0, 0
    grupo_docentes, _ = Group.objects.get_or_create(name="Docentes")
    for i, row in enumerate(reader, 2):
        try:
            if not any(row): continue
            nombres, primer_apellido, segundo_apellido, documento, email, *_ = row
            if not documento: raise ValueError("The document number is mandatory.")
            if User.objects.filter(username=documento).exists(): continue
            user = User.objects.create_user(username=documento, password=documento, email=email, first_name=str(nombres or '').upper(), last_name=f"{str(primer_apellido or '').upper()} {str(segundo_apellido or '').upper()}".strip())
            user.groups.add(grupo_docentes)
            Docente.objects.create(user=user)
            creados += 1
        except Exception as e:
            messages.warning(request, f"Error in teacher CSV row {i}: {e}")
            errores += 1
    messages.success(request, f"Teacher process completed. Created: {creados}. Errors: {errores}.")
