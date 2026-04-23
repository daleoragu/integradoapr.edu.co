# notas/reportes/utils.py
import datetime
import calendar
from ..models.perfiles import Estudiante
from ..models.academicos import Asistencia

def get_meses_for_periodo(periodo):
    """
    Devuelve una lista de tuplas (numero_mes, 'Nombre del Mes Año') 
    basada en las fechas de inicio y fin del periodo.
    """
    meses = []
    if not periodo.fecha_inicio or not periodo.fecha_fin:
        return meses
        
    fecha_actual = periodo.fecha_inicio.replace(day=1)
    fecha_fin = periodo.fecha_fin
    
    # Nombres de los meses en español
    nombres_meses = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
                     
    while fecha_actual <= fecha_fin:
        num_mes = fecha_actual.month
        año = fecha_actual.year
        nombre_mes = f"{nombres_meses[num_mes]} {año}"
        
        # Agregamos a la lista si no está repetido
        if not any(m[0] == num_mes for m in meses):
            meses.append((num_mes, nombre_mes))
            
        # Avanzar al siguiente mes
        if num_mes == 12:
            fecha_actual = fecha_actual.replace(year=año + 1, month=1)
        else:
            fecha_actual = fecha_actual.replace(month=num_mes + 1)
            
    return meses

def get_asistencia_data_for_template(asignacion, periodo, mes_num):
    """
    Prepara los estudiantes y las fechas (días hábiles) necesarios 
    para dibujar la plantilla vacía de Excel.
    """
    # 1. Obtener los estudiantes activos del curso y colegio seleccionados
    estudiantes = Estudiante.objects.filter(
        curso=asignacion.curso, 
        colegio=asignacion.colegio, 
        is_active=True
    ).order_by('user__last_name', 'user__first_name')
    
    # 2. Calcular las fechas (Lunes a Viernes) para el mes indicado
    fechas_del_mes = []
    año = periodo.fecha_inicio.year
    
    # Ajustar el año por si el periodo cruza diciembre-enero
    if mes_num < periodo.fecha_inicio.month and periodo.fecha_fin.year > periodo.fecha_inicio.year:
        año = periodo.fecha_fin.year
        
    _, num_dias = calendar.monthrange(año, mes_num)
    
    for dia in range(1, num_dias + 1):
        fecha = datetime.date(año, mes_num, dia)
        # weekday(): 0 es Lunes, 4 es Viernes. Descartamos Sábado (5) y Domingo (6)
        if fecha.weekday() < 5: 
            # Verificar que la fecha caiga exactamente dentro del periodo académico
            if periodo.fecha_inicio <= fecha <= periodo.fecha_fin:
                fechas_del_mes.append(fecha)
                
    # 3. Retornar los datos. El 'resumen' es un diccionario vacío {} porque es una plantilla en blanco
    resumen_vacio = {}
    
    return estudiantes, fechas_del_mes, resumen_vacio

def get_asistencia_data_for_report(asignacion, periodo, mes_num):
    """
    Prepara los estudiantes, fechas (días hábiles) y los datos REALES de asistencia 
    para dibujar el reporte en PDF con los datos llenos.
    """
    # 1. Obtener los estudiantes activos
    estudiantes = Estudiante.objects.filter(
        curso=asignacion.curso, 
        colegio=asignacion.colegio, 
        is_active=True
    ).order_by('user__last_name', 'user__first_name')
    
    # 2. Calcular las fechas (Lunes a Viernes) para el mes indicado
    fechas_del_mes = []
    año = periodo.fecha_inicio.year
    
    # Ajustar el año por si el periodo cruza diciembre-enero
    if mes_num < periodo.fecha_inicio.month and periodo.fecha_fin.year > periodo.fecha_inicio.year:
        año = periodo.fecha_fin.year
        
    _, num_dias = calendar.monthrange(año, mes_num)
    
    for dia in range(1, num_dias + 1):
        fecha = datetime.date(año, mes_num, dia)
        if fecha.weekday() < 5: 
            if periodo.fecha_inicio <= fecha <= periodo.fecha_fin:
                fechas_del_mes.append(fecha)
                
    # 3. Consultar las asistencias reales de la base de datos
    asistencias = Asistencia.objects.filter(
        colegio=asignacion.colegio,
        asignacion=asignacion,
        fecha__in=fechas_del_mes
    )
    
    # 4. Construir el diccionario de datos: {estudiante_id: {fecha: 'estado'}}
    resumen_asistencia = {}
    for asis in asistencias:
        if asis.estudiante_id not in resumen_asistencia:
            resumen_asistencia[asis.estudiante_id] = {}
        resumen_asistencia[asis.estudiante_id][asis.fecha] = asis.estado
        
    return estudiantes, fechas_del_mes, resumen_asistencia