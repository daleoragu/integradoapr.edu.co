# settings.py

from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- LECTURA DE VARIABLES DE ENTORNO ---
# Las claves secretas ahora se leen desde el entorno de Render, no se escriben en el código.
SECRET_KEY = os.environ.get('SECRET_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')

# En desarrollo local, DEBUG puede ser True, pero en Render siempre será False.
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = ['www.integradoapr.edu.co', 'integradoapr.edu.co', '127.0.0.1', 'integradoarp-edu-co.onrender.com', 'localhost']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'notas.apps.NotasConfig',
    'storages',  # App para la gestión de almacenamiento en S3
]

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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notas.context_processors.contador_notificaciones',
                'notas.context_processors.notificaciones_destacadas',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
}


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


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# URLs de Login
LOGIN_URL = 'portal'
LOGIN_REDIRECT_URL = 'dashboard'


# --- CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS (STATIC) Y MULTIMEDIA (MEDIA) ---

# Archivos del sitio (CSS, JS) - Servidos por WhiteNoise
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- INICIO DE LA CONFIGURACIÓN DE AMAZON S3 PARA ARCHIVOS MULTIMEDIA ---

# Credenciales de AWS (leídas desde las variables de entorno de Render)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-2') # us-east-1 como default

# Configuración para que los archivos no se sobreescriban si tienen el mismo nombre
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = 'public-read' # Permite que los archivos subidos sean públicos

# Clase que Django usará para gestionar los archivos subidos
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# URL base para los archivos de medios (apuntará a tu bucket de S3)
MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/'

# --- FIN DE LA CONFIGURACIÓN DE S3 ---
