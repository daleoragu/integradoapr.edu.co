import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # Ajusta si tu módulo de settings es diferente

import django
django.setup()

from django.conf import settings
print("DEFAULT_FILE_STORAGE:", settings.DEFAULT_FILE_STORAGE)

from django.core.files.storage import default_storage
print("default_storage:", default_storage)
print("CLASE:", default_storage.__class__)
