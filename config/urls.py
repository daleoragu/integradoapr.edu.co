# config/urls.py
# Este es el archivo de URLs principal de tu proyecto.

from django.contrib import admin
from django.urls import path, include

# --- Para servir archivos en modo de desarrollo (opcional) ---
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 1. RUTA PARA EL PANEL DE ADMINISTRACIÓN NATIVO DE DJANGO
    #    Cambiamos 'admin/' a 'super-admin/' para evitar conflictos con tus vistas.
    #    Ahora, para ver los modelos de la base de datos, irás a /super-admin/.
    path('super-admin/', admin.site.urls),

    # 2. RUTAS DE TU APLICACIÓN "NOTAS"
    #    Esta línea incluye todas las URLs de tu archivo 'notas/urls.py'.
    #    Como no tiene prefijo (es ''), buscará rutas como '/dashboard',
    #    '/admin/gestion-academica/', etc., directamente en tu app.
    path('', include('notas.urls', namespace='notas')),
]

# --- Personalización del Título y Encabezado del Admin de Django (Opcional) ---
# Esto cambia los textos que se ven en la página de /super-admin/
admin.site.site_header = "Administración del Sistema Escolar"
admin.site.site_title = "Portal de Administración"
admin.site.index_title = "Bienvenido al portal de administración"


# --- Configuración para servir archivos de medios (imágenes, etc.) en DESARROLLO ---
# Esto es útil para cuando los usuarios suben archivos.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)