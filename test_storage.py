import os
import django
from django.conf import settings
from django.core.files.base import ContentFile

# --- INICIALIZACIÓN DE DJANGO ---
# Esto es crucial. Apunta a tu archivo de configuración.
# Basado en tus archivos, la ruta correcta es 'config.settings'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Carga la configuración de Django.
django.setup()
# --- FIN DE LA INICIALIZACIÓN ---

# Ahora que Django está inicializado, podemos importar y usar sus componentes.
from django.core.files.storage import default_storage

print("--- SCRIPT DE PRUEBA PARA DIGITALOCEAN SPACES ---")

# Verifiquemos qué clase de almacenamiento se está usando AHORA.
print(f"CLASE DE ALMACENAMIENTO USADA: {type(default_storage)}")
print(f"DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
print(f"BUCKET: {settings.AWS_STORAGE_BUCKET_NAME}")
print(f"URL DE MEDIA: {settings.MEDIA_URL}")

# Crear un archivo de prueba en memoria
file_content = b'Este es el contenido de mi archivo de prueba final.'
file_name = 'test_desde_script_corregido.txt'
file_to_upload = ContentFile(file_content, name=file_name)

# Guardar el archivo usando el almacenamiento por defecto (que ahora sí es S3)
try:
    # Eliminamos el archivo si ya existe para asegurar una prueba limpia
    if default_storage.exists(file_name):
        default_storage.delete(file_name)
        print(f"Archivo existente '{file_name}' eliminado para la prueba.")

    saved_path = default_storage.save(file_name, file_to_upload)
    file_url = default_storage.url(saved_path)
    
    print(f"\n¡ÉXITO! Archivo guardado en el Space.")
    print(f"Ruta en el bucket: {saved_path}")
    print(f"URL pública del archivo: {file_url}")

except Exception as e:
    print(f"\nERROR: Ocurrió un problema al intentar subir el archivo.")
    print(f"Detalles del error: {e}")

print("\n--- FIN DEL SCRIPT ---")
