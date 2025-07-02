# config/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve # Importa la vista 'serve'

urlpatterns = [
    path('admin/', admin.site.urls),
    # Esta línea asume que todas las URLs de tu app están en 'notas.urls'
    path('', include('notas.urls')),

    # --- INICIO DE LA CORRECCIÓN PARA PRODUCCIÓN ---
    # La siguiente línea es necesaria para que Django pueda "servir" (mostrar)
    # los archivos que los usuarios suben (imágenes, documentos) cuando
    # la aplicación está en producción (DEBUG=False).
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
    # --- FIN DE LA CORRECCIÓN ---
]

# NOTA: Se elimina la condición `if settings.DEBUG:` porque necesitamos
# que esta ruta para los archivos de medios funcione siempre,
# especialmente en producción.