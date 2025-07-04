# notas/storage_backends.py

from storages.backends.s3boto3 import S3Boto3Storage

# Archivos estáticos: se almacenan en S3 bajo /static/
class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = None


# Archivos de usuario/media: se almacenan en S3 bajo /media/
class MediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = None
    file_overwrite = False


# Opcional: Archivos públicos que deben ser accesibles sin autenticación
class PublicMediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False
