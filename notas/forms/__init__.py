# notas/forms/__init__.py

# Importaciones explícitas para asegurar que Django encuentre las clases
from .observador_forms import (
    FichaEstudianteForm, 
    RegistroObservadorForm, 
    EstudianteCompromisoForm
)

# Importamos el resto de formularios usando asterisco
from .portal_forms import *
from .mensajeria_forms import *
from .admin_crud_forms import *
from .asignacion_forms import *
from .auth_forms import *