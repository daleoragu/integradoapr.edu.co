import os
from pathlib import Path

# Se utiliza python-dotenv para cargar las variables desde el archivo .env
from dotenv import load_dotenv

# Carga las variables de entorno del archivo .env al inicio.
load_dotenv()

# --- Configuración Base del Proyecto ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Configuración de Seguridad ---
SECRET_KEY = os.getenv('SECRET_KEY', 'configuracion-insegura-solo-para-desarrollo')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost 127.0.0.1 integradoapr.edu.co www.integradoapr.edu.co').split()

# --- Aplicaciones de Django ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'notas.apps.NotasConfig',
    'storages',
]

# --- Middleware ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- Configuración de URLs y WSGI ---
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# --- Plantillas (Templates) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# --- Base de Datos (Estrategia Mixta) ---
# Se usará PostgreSQL en producción (cuando DEBUG=False)
# y SQLite para desarrollo local (cuando DEBUG=True) para evitar problemas de entorno.

if DEBUG:
    print("✅ MODO DEBUG: Usando base de datos SQLite local.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    print("🚀 MODO PRODUCCIÓN: Usando base de datos PostgreSQL.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
            'CONN_MAX_AGE': 60, # Optimización para producción
        }
    }

# --- Validación de Contraseñas ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Internacionalización ---
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# --- Archivos Estáticos (CSS, JavaScript, Imágenes de la plantilla) ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- Almacenamiento de Archivos Multimedia (Subidos por usuarios) ---
USE_B2 = os.getenv("USE_B2", "false").lower() in ("true", "1", "yes")

print("✅ INICIANDO CONFIGURACIÓN DE ALMACENAMIENTO...")
if USE_B2:
    print("✅ USANDO ALMACENAMIENTO EN BACKBLAZE B2.")
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # --- CORRECCIÓN DE URLS PARA BACKBLAZE B2 (MÉTODO ROBUSTO) ---
    B2_REGION = os.getenv("B2_REGION")
    B2_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")

    # Limpia la variable de región por si el usuario dejó el dominio completo
    if B2_REGION and 'backblazeb2.com' in B2_REGION:
        try:
            # Extrae 'us-east-005' de 's3.us-east-005.backblazeb2.com'
            B2_REGION = B2_REGION.split('.')[1]
        except IndexError:
            B2_REGION = 'us-east-005' # Fallback seguro

    AWS_ACCESS_KEY_ID = os.getenv("B2_APPLICATION_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("B2_APPLICATION_KEY")
    AWS_STORAGE_BUCKET_NAME = B2_BUCKET_NAME
    AWS_S3_REGION_NAME = B2_REGION
    
    # Usar AWS_S3_CUSTOM_DOMAIN para forzar la URL correcta.
    # Esto evita que django-storages construya una URL incorrecta a partir del endpoint.
    AWS_S3_CUSTOM_DOMAIN = f'{B2_BUCKET_NAME}.s3.{B2_REGION}.backblazeb2.com'
    
    # AWS_S3_LOCATION para organizar los archivos en una carpeta 'media/' dentro del bucket.
    AWS_S3_LOCATION = 'media'
    
    # La URL de medios ahora se basa en el dominio personalizado y la ubicación.
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_S3_LOCATION}/'
    
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_S3_VERIFY = True

else:
    print("✅ USANDO ALMACENAMIENTO LOCAL (para desarrollo).")
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# --- Clave Primaria por Defecto ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Configuraciones de Seguridad para Producción ---
if not DEBUG:
    print("🚀 APLICANDO CONFIGURACIONES DE SEGURIDAD ADICIONALES PARA PRODUCCIÓN.")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
