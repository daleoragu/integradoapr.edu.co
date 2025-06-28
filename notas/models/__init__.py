# notas/models/__init__.py

# Este archivo importa todos los modelos de sus respectivos archivos
# y los hace disponibles para que puedan ser importados desde 'notas.models'.

from .perfiles import Curso, Docente, Estudiante, FichaEstudiante
from .academicos import (
    AreaConocimiento, Materia, PeriodoAcademico, AsignacionDocente,
    Calificacion, IndicadorLogroPeriodo, ReporteParcial, Observacion,
    PlanDeMejoramiento, Asistencia, InasistenciasManualesPeriodo,
    ConfiguracionSistema, PublicacionBoletin, PublicacionBoletinFinal
)
from .comunicaciones import Mensaje, RegistroObservador, Notificacion

# CORRECCIÓN: Se añaden todos los modelos del portal, incluyendo el nuevo 'ImagenCarrusel'.
from .portal_models import DocumentoPublico, FotoGaleria, Noticia, ImagenCarrusel

# La variable __all__ es una buena práctica que define qué nombres
# se exportan cuando se hace 'from .models import *'.
__all__ = [
    'Curso', 'Docente', 'Estudiante', 'FichaEstudiante',
    'AreaConocimiento', 'Materia', 'PeriodoAcademico', 'AsignacionDocente',
    'Calificacion', 'IndicadorLogroPeriodo', 'ReporteParcial', 'Observacion',
    'PlanDeMejoramiento', 'Asistencia', 'InasistenciasManualesPeriodo',
    'ConfiguracionSistema', 'PublicacionBoletin', 'PublicacionBoletinFinal',
    'Mensaje', 'RegistroObservador', 'Notificacion',
    'DocumentoPublico', 'FotoGaleria', 'Noticia', 'ImagenCarrusel',
]
