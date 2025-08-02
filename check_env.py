# check_env.py
import os
from dotenv import load_dotenv

# Cargamos las variables del archivo .env
load_dotenv()

# Intentamos leer una de las variables
bucket_name = os.getenv('DO_SPACES_BUCKET_NAME')

if bucket_name:
    print(f"✅ Éxito: El archivo .env se leyó correctamente.")
    print(f"   El nombre del bucket es: {bucket_name}")
else:
    print(f"❌ Error: No se pudo leer la variable DO_SPACES_BUCKET_NAME del archivo .env.")
    print(f"   Asegúrate de que el archivo .env está en la misma carpeta que este script y tiene el formato correcto.")