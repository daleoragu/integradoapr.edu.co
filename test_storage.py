import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings
print("DEFAULT_FILE_STORAGE:", settings.DEFAULT_FILE_STORAGE)
from django.core.files.storage import default_storage
print("default_storage:", default_storage)

from django.core.files.base import ContentFile
name = default_storage.save('test_final_spacess.txt', ContentFile(b"Prueba storage directo script"))
print("Archivo guardado:", name)
