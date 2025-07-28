# notas/middleware.py
from .models import Colegio

class ColegioMiddleware:
    """
    Middleware que identifica el colegio activo basándose en el subdominio (wildcard).
    Esta versión está diseñada para funcionar con un registro DNS comodín (*.tu_dominio.com).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # No ejecutar este middleware para rutas del admin para evitar conflictos.
        if request.path.startswith('/admin'):
            request.colegio = None
            return self.get_response(request)

        host = request.get_host().split(':')[0].lower()
        
        # Define tu dominio principal. Es importante para saber qué parte es el subdominio.
        # ¡Asegúrate de que este dominio coincida con el tuyo!
        main_domain = 'mcolegio.com.co'
        
        request.colegio = None
        
        try:
            # Comprueba si el host termina con el dominio principal y no es el dominio principal en sí.
            if host.endswith(main_domain) and host != main_domain and host != f'www.{main_domain}':
                # Extrae la parte del subdominio.
                # Ejemplo: de 'colegio-x.mcolegio.com.co' -> 'colegio-x'
                slug = host.replace(f'.{main_domain}', '')
                
                # Busca el colegio usando el slug extraído.
                try:
                    request.colegio = Colegio.objects.get(slug=slug)
                except Colegio.DoesNotExist:
                    # El subdominio existe en DNS pero no hay un colegio con ese slug.
                    # request.colegio permanecerá como None y la vista puede mostrar un 404.
                    pass
            
            # Lógica para desarrollo en localhost (opcional pero útil)
            elif host.endswith('.localhost'):
                slug = host.split('.')[0]
                try:
                    request.colegio = Colegio.objects.get(slug=slug)
                except Colegio.DoesNotExist:
                    pass

            # Si se accede al dominio principal (ej: mcolegio.com.co), puedes
            # opcionalmente cargar un colegio por defecto o dejarlo en None para
            # mostrar una página de bienvenida general.
            # else:
            #     # Opcional: buscar un colegio principal si se accede al dominio raíz
            #     try:
            #         request.colegio = Colegio.objects.get(es_principal=True)
            #     except (Colegio.DoesNotExist, AttributeError):
            #         pass

        except Exception:
            # Si ocurre cualquier error inesperado, se ignora para no romper el sitio.
            pass
        
        response = self.get_response(request)
        return response
