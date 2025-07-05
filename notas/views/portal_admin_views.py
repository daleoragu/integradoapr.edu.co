# notas/views/portal_admin_views.py
import os # Asegúrate de que os esté importado al principio del archivo
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

# Se importan todos los modelos y formularios necesarios para el panel
from ..models import DocumentoPublico, FotoGaleria, Noticia, ImagenCarrusel
from ..forms import DocumentoPublicoForm, FotoGaleriaForm, NoticiaForm, ImagenCarruselForm

def es_admin_o_docente(user):
    # Esta función permite el acceso a Superusuarios y a miembros del grupo 'Docentes'
    return user.is_superuser or user.groups.filter(name='Docentes').exists()

@user_passes_test(es_admin_o_docente)
def configuracion_portal_vista(request):
    """
    Carga el panel principal de configuración del portal.
    """
    return render(request, 'notas/admin_portal/configuracion_portal.html')

# --- VISTAS PARA DOCUMENTOS ---
@user_passes_test(es_admin_o_docente)
def gestion_documentos_vista(request):
    if request.method == 'POST':
        form = DocumentoPublicoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Documento guardado exitosamente.')
            return redirect('gestion_documentos')
    else:
        form = DocumentoPublicoForm()
    documentos = DocumentoPublico.objects.all()
    context = {'form': form, 'documentos': documentos, 'page_title': 'Gestionar Documentos'}
    return render(request, 'notas/admin_portal/gestion_documentos.html', context)

@user_passes_test(es_admin_o_docente)
def eliminar_documento_vista(request, pk):
    documento = get_object_or_404(DocumentoPublico, pk=pk)
    if request.method == 'POST':
        documento.delete()
        messages.success(request, 'Documento eliminado exitosamente.')
    return redirect('gestion_documentos')

# --- VISTAS PARA LA GALERÍA ---
@user_passes_test(es_admin_o_docente)
def gestion_galeria_vista(request):
    if request.method == 'POST':
        form = FotoGaleriaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Foto añadida a la galería.')
            return redirect('gestion_galeria')
    else:
        form = FotoGaleriaForm()
    fotos = FotoGaleria.objects.all()
    context = {'form': form, 'fotos': fotos, 'page_title': 'Gestionar Galería'}
    return render(request, 'notas/admin_portal/gestion_galeria.html', context)

@user_passes_test(es_admin_o_docente)
def eliminar_foto_vista(request, pk):
    foto = get_object_or_404(FotoGaleria, pk=pk)
    if request.method == 'POST':
        foto.delete()
        messages.success(request, 'Foto eliminada de la galería.')
    return redirect('gestion_galeria')

# --- VISTAS PARA NOTICIAS ---
@user_passes_test(es_admin_o_docente)
def gestion_noticias_vista(request):
    noticias = Noticia.objects.all()
    context = {'noticias': noticias, 'page_title': 'Gestionar Noticias'}
    return render(request, 'notas/admin_portal/gestion_noticias.html', context)

@user_passes_test(es_admin_o_docente)
def crear_noticia_vista(request):
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES)
        if form.is_valid():
            noticia = form.save(commit=False)
            noticia.autor = request.user
            noticia.save()
            messages.success(request, 'Noticia creada como BORRADOR. Ahora puedes publicarla desde la lista.')
            return redirect('gestion_noticias')
    else:
        form = NoticiaForm()
    context = {'form': form, 'accion': 'Crear', 'page_title': 'Crear Noticia'}
    return render(request, 'notas/admin_portal/formulario_noticia.html', context)

@user_passes_test(es_admin_o_docente)
def editar_noticia_vista(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)
    if request.method == 'POST':
        form = NoticiaForm(request.POST, request.FILES, instance=noticia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Noticia actualizada exitosamente.')
            return redirect('gestion_noticias')
    else:
        form = NoticiaForm(instance=noticia)
    context = {'form': form, 'accion': 'Editar', 'page_title': f'Editando: {noticia.titulo}'}
    return render(request, 'notas/admin_portal/formulario_noticia.html', context)

@user_passes_test(es_admin_o_docente)
def eliminar_noticia_vista(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)
    if request.method == 'POST':
        noticia.delete()
        messages.success(request, 'Noticia eliminada exitosamente.')
    return redirect('gestion_noticias')

@user_passes_test(es_admin_o_docente)
def publicar_noticia_vista(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)
    if request.method == 'POST':
        if noticia.estado == 'BORRADOR':
            noticia.estado = 'PUBLICADO'
            messages.success(request, f"La noticia '{noticia.titulo}' ha sido publicada.")
        else:
            noticia.estado = 'BORRADOR'
            messages.info(request, f"La noticia '{noticia.titulo}' ha sido movida a borradores.")
        noticia.save()
    return redirect('gestion_noticias')

# --- VISTAS PARA GESTIONAR EL CARRUSEL ---
# notas/views/portal_admin_views.py
import os
import logging # Importar logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from ..models import DocumentoPublico, FotoGaleria, Noticia, ImagenCarrusel
from ..forms import DocumentoPublicoForm, FotoGaleriaForm, NoticiaForm, ImagenCarruselForm

# Configurar el logger para este archivo
logger = logging.getLogger(__name__)

def es_admin_o_docente(user):
    return user.is_superuser or user.groups.filter(name='Docentes').exists()

@user_passes_test(es_admin_o_docente)
def configuracion_portal_vista(request):
    return render(request, 'notas/admin_portal/configuracion_portal.html')

# ... (tus otras vistas no cambian) ...

# --- VISTAS PARA GESTIONAR EL CARRUSEL (CON LOGGING DETALLADO) ---
@user_passes_test(es_admin_o_docente)
def gestion_carrusel_vista(request):
    logger.info("--- Iniciando gestion_carrusel_vista ---")
    if request.method == 'POST':
        logger.info("Petición POST recibida para el carrusel.")
        form = ImagenCarruselForm(request.POST, request.FILES)
        if form.is_valid():
            logger.info("El formulario es válido. Procediendo a guardar.")
            try:
                # Guardamos el formulario sin hacer commit a la base de datos todavía
                nueva_imagen = form.save(commit=False)
                logger.info("Objeto del modelo creado en memoria.")
                
                # Ahora guardamos el objeto completo en la base de datos.
                # El guardado del archivo en B2 ocurre aquí, dentro de form.save().
                nueva_imagen.save()
                logger.info(f"form.save() completado. Objeto guardado en DB. Ruta de imagen: {nueva_imagen.imagen.name}")
                
                messages.success(request, f'Formulario procesado. La imagen debería estar en: {nueva_imagen.imagen.name}')
                return redirect('gestion_carrusel')

            except Exception as e:
                # Si algo falla durante la subida, lo registraremos
                logger.error(f"¡EXCEPCIÓN ATRAPADA DURANTE EL GUARDADO! Error: {e}", exc_info=True)
                messages.error(request, f'ERROR AL PROCESAR EL FORMULARIO: {e}')
        else:
            # Si el formulario no es válido, lo registramos
            logger.warning(f"El formulario no es válido. Errores: {form.errors.as_json()}")
            messages.warning(request, f'El formulario no es válido: {form.errors.as_json()}')
    else:
        form = ImagenCarruselForm()
    
    imagenes = ImagenCarrusel.objects.all()
    context = { 'form': form, 'imagenes': imagenes, 'page_title': 'Gestionar Carrusel' }
    return render(request, 'notas/admin_portal/gestion_carrusel.html', context)

# ... (el resto de tus vistas no cambian) ...
@user_passes_test(es_admin_o_docente)
def eliminar_imagen_carrusel_vista(request, pk):
    imagen = get_object_or_404(ImagenCarrusel, pk=pk)
    if request.method == 'POST':
        imagen.delete()
        messages.success(request, 'Imagen eliminada del carrusel.')
    return redirect('gestion_carrusel')

# ... (y el resto de tus vistas) ...
