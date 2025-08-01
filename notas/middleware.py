# notas/middleware.py
from .models import Colegio

class ColegioMiddleware:
    """
    Middleware que identifica el colegio activo basándose en el subdominio.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # --- ¡ESTA ES LA CORRECCIÓN CLAVE! ---
        # Ahora solo ignoramos el panel de SUPER-ADMIN, permitiendo que
        # nuestras vistas personalizadas en /admin/ funcionen correctamente.
        if request.path.startswith('/super-admin/'):
            request.colegio = None
            return self.get_response(request)

        host = request.get_host().split(':')[0].lower()
        
        # Define tu dominio principal.
        # Asegúrate de que este dominio coincida con el tuyo en producción.
        main_domain = 'mcolegio.com.co'
        
        request.colegio = None
        
        try:
            # Lógica para producción (ej: colegio-x.mcolegio.com.co)
            if host.endswith(main_domain) and host != main_domain and host != f'www.{main_domain}':
                # Extrae el 'slug' del subdominio.
                slug = host.replace(f'.{main_domain}', '')
                request.colegio = Colegio.objects.get(slug=slug)
            
            # Lógica para desarrollo en localhost (ej: colegio-bilingue-san-sebastian.localhost)
            elif host.endswith('.localhost'):
                slug = host.split('.')[0]
                request.colegio = Colegio.objects.get(slug=slug)

        except Colegio.DoesNotExist:
            # Si el subdominio existe pero no hay un colegio con ese slug en la BD,
            # request.colegio permanecerá como None.
            pass
        except Exception:
            # Si ocurre cualquier otro error, se ignora para no romper el sitio.
            pass
        
        response = self.get_response(request)
        return response
