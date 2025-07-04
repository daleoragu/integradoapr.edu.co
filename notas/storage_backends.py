# notas/storage_backends.py

from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class PublicMediaStorage(S3Boto3Storage):
    """
    Almacenamiento para archivos públicos en S3.
    """
    default_acl = 'public-read'
    file_overwrite = False

    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = settings.AWS_STORAGE_BUCKET_NAME
        kwargs['region_name'] = settings.AWS_S3_REGION_NAME
        kwargs['custom_domain'] = f"{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com"
        super().__init__(*args, **kwargs)
