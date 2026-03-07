from django.urls import path
from . import views

app_name = 'elecciones'

urlpatterns = [
    path('', views.dashboard_elecciones, name='dashboard'),
    path('panel/', views.panel_admin, name='panel_admin'),
    
    # --- GESTIÓN DE PUESTOS ---
    path('panel/puesto/nuevo/', views.crear_puesto, name='crear_puesto'),
    path('panel/puesto/editar/<int:puesto_id>/', views.editar_puesto, name='editar_puesto'),
    path('panel/puesto/eliminar/<int:puesto_id>/', views.eliminar_puesto, name='eliminar_puesto'),
    
    # --- GESTIÓN DE MESAS Y JURADOS ---
    path('panel/mesa/nueva/', views.crear_mesa, name='crear_mesa'),
    path('panel/mesa/editar/<int:mesa_id>/', views.editar_mesa, name='editar_mesa'),
    path('panel/mesa/eliminar/<int:mesa_id>/', views.eliminar_mesa, name='eliminar_mesa'),
    path('panel/jurado/nuevo/', views.crear_jurado, name='crear_jurado'),
    
    # --- GESTIÓN DE PARTIDOS ---
    path('panel/partido/nuevo/', views.crear_partido, name='crear_partido'),
    path('panel/partido/editar/<int:partido_id>/', views.editar_partido, name='editar_partido'),
    path('panel/partido/eliminar/<int:partido_id>/', views.eliminar_partido, name='eliminar_partido'),
    
    # --- GESTIÓN DE CANDIDATOS ---
    path('panel/candidato/nuevo/', views.crear_candidato, name='crear_candidato'),
    path('panel/candidato/editar/<int:candidato_id>/', views.editar_candidato, name='editar_candidato'),
    path('panel/candidato/eliminar/<int:candidato_id>/', views.eliminar_candidato, name='eliminar_candidato'),
    
    # --- CARGAS AUTOMÁTICAS ---
    path('panel/auto-cargar-tarjeton/', views.cargar_tarjeton_camara_tolima, name='cargar_tarjeton_camara'),
    path('panel/auto-cargar-senado/', views.cargar_tarjeton_senado, name='cargar_tarjeton_senado'),
    path('panel/auto-cargar-consulta/', views.cargar_tarjeton_consulta, name='cargar_tarjeton_consulta'),
    
    # RUTA 1: El Tarjetón (Táctil)
    path('jurado/tarjeton/', views.digitar_votos, name='digitar_votos'),
    # RUTA 2: El Formulario E-14 (Clásico en tabla)
    path('jurado/e14/', views.ver_e14, name='ver_e14'),
    
    path('logout/', views.logout_jurado, name='logout'),
]