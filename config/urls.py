# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Volvemos a usar el admin por defecto de Django
    path('admin/', admin.site.urls),
    
    # Esta línea conecta con todas las URLs de tu aplicación 'notas'
    path('', include('notas.urls')),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
