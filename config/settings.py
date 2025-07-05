import os
from pathlib import Path
import dj_database_url # Importar la librería para la URL de la base de datos

# Se utiliza python-dotenv para cargar las variables desde el archivo .env
from dotenv import load_dotenv

# Carga las variables de entorno del archivo .env al inicio.
load_dotenv()

# --- Configuración Base del Proyecto ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Configuración de Seguridad ---
SECRET_KEY = os.getenv('SECRET_KEY', 'configuracion-insegura-solo-para-desarrollo')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

# --- CORRECCIÓN DE ALLOWED_HOSTS ---
# Se leen los hosts desde la variable de entorno de Render.
# Si no existe, se usa una lista segura que incluye tus dominios.
ALLOWED_HOSTS_str = os.getenv('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_str.split(',') if host.strip()]

# Añadimos los dominios de Render y el tuyo por defecto para asegurar que siempre funcionen.
# Render usa un dominio .onrender.com para sus servicios.
if not DEBUG:
    ALLOWED_HOSTS.extend([
        'integradoapr.edu.co',
        'www.integradoapr.edu.co',
        os.getenv('RENDER_EXTERNAL_HOSTNAME') # Añade el dominio de Render automáticamente
    ])
    # Eliminar None si RENDER_EXTERNAL_HOSTNAME no está definido
    ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host]


# --- Aplicaciones de Django ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Para que WhiteNoise sirva estáticos en desarrollo
    'django.contrib.staticfiles',
    'notas.apps.NotasConfig',
    'storages',
]

# --- Middleware ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # WhiteNoise debe estar aquí
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
if DEBUG:
    print("✅ MODO DEBUG: Usando base de datos SQLite local.")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    print("🚀 MODO PRODUCCIÓN: Usando base de datos PostgreSQL desde DATABASE_URL.")
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=60,
            ssl_require=True
        )
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

if USE_B2:
    print("✅ USANDO ALMACENAMIENTO EN BACKBLAZE B2.")
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    B2_REGION = os.getenv("B2_REGION")
    B2_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")

    if B2_REGION and 'backblazeb2.com' in B2_REGION:
        try:
            B2_REGION = B2_REGION.split('.')[1]
        except IndexError:
            B2_REGION = 'us-east-005'

    AWS_ACCESS_KEY_ID = os.getenv("B2_APPLICATION_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("B2_APPLICATION_KEY")
    AWS_STORAGE_BUCKET_NAME = B2_BUCKET_NAME
    AWS_S3_REGION_NAME = B2_REGION
    AWS_S3_CUSTOM_DOMAIN = f'{B2_BUCKET_NAME}.s3.{B2_REGION}.backblazeb2.com'
    AWS_S3_LOCATION = 'media'
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
