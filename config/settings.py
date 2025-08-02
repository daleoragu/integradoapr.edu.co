import os
from pathlib import Path
import dj_database_url

# --- INICIO DE LA SOLUCIÓN DEFINITIVA ---
# 1. Construimos la ruta explícita al archivo .env
#    BASE_DIR apunta a la carpeta raíz del proyecto.
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'

# 2. Le pasamos la ruta explícita a load_dotenv
from dotenv import load_dotenv
load_dotenv(dotenv_path=dotenv_path)
# --- FIN DE LA SOLUCIÓN DEFINITIVA ---


SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'tu-clave-secreta-para-desarrollo')

# DEBUG se controla con una variable de entorno. En DigitalOcean será 'False'.
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    'mcolegio.com.co',
    '.mcolegio.com.co',
    'localhost',
    '127.0.0.1',
    '.localhost',
    'integradoapr.edu.co',
]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'notas.apps.NotasConfig',
    'crispy_forms',
    'crispy_bootstrap5',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'notas.middleware.ColegioMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'notas.context_processors.contador_notificaciones',
                'notas.context_processors.notificaciones_destacadas',
                'notas.context_processors.colegio_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# --- Base de Datos ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        ssl_require=True,
        default=DATABASE_URL
    )

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# --- ARCHIVOS ESTÁTICOS (CSS, JS) ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- ARCHIVOS DE MEDIOS (Subidos por usuarios) ---

# Por defecto, se usa el almacenamiento local.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Si las variables de entorno para Spaces existen, se sobreescribe la configuración.
AWS_STORAGE_BUCKET_NAME = os.getenv('DO_SPACES_BUCKET_NAME')
if AWS_STORAGE_BUCKET_NAME:
    # Si ves este mensaje en la consola, ¡el .env está funcionando!
    print(f"✅ Conectando a DigitalOcean Spaces. Bucket: {AWS_STORAGE_BUCKET_NAME}")

    AWS_ACCESS_KEY_ID = os.getenv('DO_SPACES_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = os.getenv('DO_SPACES_SECRET_KEY')
    AWS_S3_REGION_NAME = os.getenv('DO_SPACES_REGION')
    
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_S3_ENDPOINT_URL = f'https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com'
    
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_QUERYSTRING_AUTH = False 
    
    AWS_LOCATION = 'media' 
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.digitaloceanspaces.com/{AWS_LOCATION}/'
    MEDIA_ROOT = '' 
else:
    # Mensaje para saber que estás en modo local
    print("⚪️ Usando almacenamiento local para archivos de medios.")

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URL de Login para proteger vistas
LOGIN_URL = '/admin/login/'
