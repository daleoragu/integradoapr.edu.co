from django.urls import path
from . import views

app_name = 'elecciones'

urlpatterns = [
    path('', views.dashboard_elecciones, name='dashboard'),
    path('panel/', views.panel_admin, name='panel_admin'),
    path('panel/puesto/nuevo/', views.crear_puesto, name='crear_puesto'),
    path('panel/mesa/nueva/', views.crear_mesa, name='crear_mesa'),
    path('panel/jurado/nuevo/', views.crear_jurado, name='crear_jurado'),
    
    path('panel/partido/nuevo/', views.crear_partido, name='crear_partido'),
    path('panel/partido/editar/<int:partido_id>/', views.editar_partido, name='editar_partido'),
    path('panel/candidato/nuevo/', views.crear_candidato, name='crear_candidato'),
    path('panel/auto-cargar-tarjeton/', views.cargar_tarjeton_camara_tolima, name='cargar_tarjeton_camara'),
    
    # RUTA 1: El Tarjetón (Táctil)
    path('jurado/tarjeton/', views.digitar_votos, name='digitar_votos'),
    # RUTA 2: El Formulario E-14 (Clásico en tabla)
    path('jurado/e14/', views.ver_e14, name='ver_e14'),
    
    path('logout/', views.logout_jurado, name='logout'),
]