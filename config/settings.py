import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar archivo .env desde la raíz del proyecto
load_dotenv(BASE_DIR / '.env')

# Variables de entorno
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')


# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Para que whitenoise funcione bien en desarrollo
    'django.contrib.staticfiles',
    'storages',
    'notas',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Debe ir justo después de SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Base de datos
# Render establece la variable DATABASE_URL automáticamente.
DATABASES = {
    'default': dj_database_url.config(
        conn_max_age=600,
        ssl_require=os.environ.get('DATABASE_SSL_REQUIRE', 'True').lower() == 'true'
    )
}

# --- SECCIÓN DE ARCHIVOS ESTÁTICOS Y MEDIA CORREGIDA ---

# URL para referenciar archivos estáticos en las plantillas (CSS, JavaScript, Imágenes)
STATIC_URL = '/static/'
# Directorio donde `collectstatic` reunirá todos los archivos estáticos para producción.
# Esta configuración es AHORA GLOBAL y siempre está definida, solucionando el error.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# URL para manejar los archivos subidos por los usuarios.
MEDIA_URL = '/media/'
# Directorio donde se guardarán los archivos subidos por los usuarios en desarrollo.
MEDIA_ROOT = BASE_DIR / 'media'


# Lógica para cambiar el almacenamiento en producción (S3) vs desarrollo/whitenoise
USE_S3 = os.environ.get('USE_S3', 'False').lower() == 'true'

if USE_S3:
    # Configuración para producción con Amazon S3
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False

    # Almacenamiento para estáticos (collectstatic los subirá a S3) y media (archivos de usuario)
    STATICFILES_STORAGE = 'config.storage_backends.StaticStorage'
    DEFAULT_FILE_STORAGE = 'config.storage_backends.MediaStorage'
else:
    # Configuración para desarrollo o despliegue con Whitenoise (como en Render sin S3)
    # Whitenoise se encarga de servir los archivos desde la carpeta definida en STATIC_ROOT.
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Autenticación
LOGIN_URL = '/accounts/login/'

# Internacionalización
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# Validadores de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
