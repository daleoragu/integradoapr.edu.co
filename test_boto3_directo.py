import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

print("--- PRUEBA DE CONEXIÓN DIRECTA A DIGITALOCEAN SPACES CON BOTO3 ---")

# --- 1. Cargar configuración desde .env ---
access_key = os.getenv('DO_SPACES_ACCESS_KEY')
secret_key = os.getenv('DO_SPACES_SECRET_KEY')
bucket_name = os.getenv('DO_SPACES_BUCKET_NAME')
region_name = os.getenv('DO_SPACES_REGION')
endpoint_url = f'https://{region_name}.digitaloceanspaces.com'

# Verificar que las variables se cargaron
if not all([access_key, secret_key, bucket_name, region_name]):
    print("\nERROR: Faltan una o más variables de entorno en tu archivo .env.")
    print("Asegúrate de que DO_SPACES_ACCESS_KEY, DO_SPACES_SECRET_KEY, DO_SPACES_BUCKET_NAME y DO_SPACES_REGION estén definidas.")
    exit()

print(f"Bucket: {bucket_name}")
print(f"Región: {region_name}")
print(f"Endpoint: {endpoint_url}")

# --- 2. Crear el cliente de S3 ---
session = boto3.session.Session()
client = session.client('s3',
                        region_name=region_name,
                        endpoint_url=endpoint_url,
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key)

# --- 3. Intentar subir un archivo ---
file_name_to_upload = 'test_directo_boto3.txt'
file_content = b'Si ves este archivo, la conexion con boto3 fue exitosa.'
object_key = f'media/{file_name_to_upload}' # Subimos dentro de la carpeta 'media'

try:
    print(f"\nIntentando subir el archivo '{file_name_to_upload}' al bucket...")
    
    client.put_object(Bucket=bucket_name,
                      Key=object_key,
                      Body=file_content,
                      ACL='public-read') # Hacemos el archivo público

    file_url = f"{endpoint_url}/{bucket_name}/{object_key}"
    print("\n¡ÉXITO! El archivo se subió correctamente.")
    print(f"URL del archivo: https://{bucket_name}.{region_name}.digitaloceanspaces.com/media/{file_name_to_upload}")

except ClientError as e:
    error_code = e.response['Error']['Code']
    print("\nERROR AL SUBIR EL ARCHIVO:")
    print(f"Código de error de DigitalOcean/AWS: {error_code}")
    print(f"Mensaje completo: {e}")
    if error_code == 'AccessDenied':
        print("\nCAUSA PROBABLE: ¡Problema de permisos! La clave de API no tiene permiso para escribir (PutObject) en el bucket.")
        print("Por favor, revisa los permisos de la clave en el panel de control de DigitalOcean.")
    elif error_code == 'NoSuchBucket':
        print("\nCAUSA PROBABLE: El nombre del bucket no es correcto o no existe en esta región.")

except Exception as e:
    print(f"\nOcurrió un error inesperado: {e}")

print("\n--- FIN DE LA PRUEBA ---")
