from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum
from .models import Corporacion, PuestoVotacion, Mesa, Partido, Candidato, FichaEscrutinio, DetalleVoto
from .forms import PuestoVotacionForm, MesaForm, JuradoForm, PartidoForm, CandidatoForm

def dashboard_elecciones(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        password = request.POST.get('password')
        user = authenticate(request, username=cedula, password=password)
        if user is not None:
            login(request, user)
            return redirect('elecciones:panel_admin')
        else:
            messages.error(request, 'Cédula o contraseña incorrecta. Por favor, verifique.')
            return redirect('elecciones:dashboard')

    corp_nombre = request.GET.get('corp', 'CAMARA')
    corporacion_obj, _ = Corporacion.objects.get_or_create(nombre=corp_nombre)

    total_mesas = Mesa.objects.count()
    fichas = FichaEscrutinio.objects.filter(corporacion=corporacion_obj)
    mesas_informadas = fichas.count()
    porcentaje_mesas = (mesas_informadas / total_mesas * 100) if total_mesas > 0 else 0

    votos_blancos = fichas.aggregate(Sum('votos_en_blanco'))['votos_en_blanco__sum'] or 0
    votos_nulos = fichas.aggregate(Sum('votos_nulos'))['votos_nulos__sum'] or 0
    votos_no_marcados = fichas.aggregate(Sum('votos_no_marcados'))['votos_no_marcados__sum'] or 0

    resultados_partidos = []
    top_candidatos = []
    votos_validos_solo_candidatos = 0

    for partido in Partido.objects.all():
        votos_partido = 0
        candidatos_partido = []
        
        candidatos_del_partido = Candidato.objects.filter(partido=partido, corporacion=corporacion_obj)
        if not candidatos_del_partido.exists(): continue

        for cand in candidatos_del_partido:
            votos_cand = DetalleVoto.objects.filter(ficha__in=fichas, candidato=cand).aggregate(Sum('cantidad'))['cantidad__sum'] or 0
            votos_partido += votos_cand
            candidatos_partido.append({'candidato': cand, 'votos': votos_cand})
            top_candidatos.append({'candidato': cand, 'partido': partido, 'votos': votos_cand})

        votos_validos_solo_candidatos += votos_partido
        resultados_partidos.append({
            'partido': partido, 'votos': votos_partido,
            'candidatos': sorted(candidatos_partido, key=lambda x: x['votos'], reverse=True)
        })

    resultados_partidos = sorted(resultados_partidos, key=lambda x: x['votos'], reverse=True)
    top_candidatos = sorted(top_candidatos, key=lambda x: x['votos'], reverse=True)
    votos_validos = votos_validos_solo_candidatos + votos_blancos

    for item in resultados_partidos:
        item['porcentaje'] = (item['votos'] / votos_validos * 100) if votos_validos > 0 else 0
        item['str_porcentaje'] = str(round(item['porcentaje'], 2)).replace(',', '.')
        for cand in item['candidatos']:
            cand['porcentaje'] = (cand['votos'] / votos_validos * 100) if votos_validos > 0 else 0
            cand['str_porcentaje'] = str(round(cand['porcentaje'], 2)).replace(',', '.')

    for cand in top_candidatos:
        cand['porcentaje'] = (cand['votos'] / votos_validos * 100) if votos_validos > 0 else 0
        cand['str_porcentaje'] = str(round(cand['porcentaje'], 2)).replace(',', '.')

    context = {
        'titulo': 'Escrutinio Local - Honda, Tolima',
        'total_mesas': total_mesas, 'mesas_informadas': mesas_informadas, 'porcentaje_mesas': round(porcentaje_mesas, 2),
        'votos_validos': votos_validos, 'votos_blancos': votos_blancos, 'votos_nulos': votos_nulos, 'votos_no_marcados': votos_no_marcados,
        'resultados_partidos': resultados_partidos, 'top_candidatos': top_candidatos,
        'corp_actual': corp_nombre, 'nombre_corporacion': corporacion_obj.get_nombre_display(),
    }
    return render(request, 'elecciones/index.html', context)

def logout_jurado(request):
    logout(request)
    return redirect('elecciones:dashboard')

@login_required(login_url='/elecciones2026/')
def panel_admin(request):
    if not request.user.is_superuser: return redirect('elecciones:digitar_votos')
    Corporacion.objects.get_or_create(nombre='CAMARA')
    Corporacion.objects.get_or_create(nombre='SENADO')
    Corporacion.objects.get_or_create(nombre='CONSULTA')
        
    puestos = PuestoVotacion.objects.all()
    mesas = Mesa.objects.all().select_related('puesto', 'responsable').order_by('puesto', 'numero_mesa')
    partidos = Partido.objects.all()
    candidatos = Candidato.objects.all().select_related('partido', 'corporacion').order_by('corporacion', 'partido', 'numero_tarjeton')
    
    return render(request, 'elecciones/panel_admin.html', {
        'puestos': puestos, 'mesas': mesas, 'partidos': partidos, 'candidatos': candidatos
    })

# --- GESTIÓN DE PUESTOS ---
@login_required(login_url='/elecciones2026/')
def crear_puesto(request):
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    if request.method == 'POST':
        form = PuestoVotacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Puesto creado correctamente.')
            return redirect('elecciones:panel_admin')
    else:
        form = PuestoVotacionForm()
    return render(request, 'elecciones/form_generico.html', {'form': form, 'titulo': 'Agregar Puesto', 'icono': 'fa-school'})

@login_required(login_url='/elecciones2026/')
def editar_puesto(request, puesto_id):
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    puesto = get_object_or_404(PuestoVotacion, id=puesto_id)
    if request.method == 'POST':
        form = PuestoVotacionForm(request.POST, instance=puesto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Puesto actualizado correctamente.')
            return redirect('elecciones:panel_admin')
    else:
        form = PuestoVotacionForm(instance=puesto)
    return render(request, 'elecciones/form_generico.html', {'form': form, 'titulo': f'Editar Puesto: {puesto.nombre}', 'icono': 'fa-edit'})

@login_required(login_url='/elecciones2026/')
def eliminar_puesto(request, puesto_id):
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    puesto = get_object_or_404(PuestoVotacion, id=puesto_id)
    puesto.delete()
    messages.success(request, 'Puesto eliminado correctamente.')
    return redirect('elecciones:panel_admin')


# --- GESTIÓN DE MESAS Y JURADOS ---
@login_required(login_url='/elecciones2026/')
def crear_mesa(request):
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mesa creada correctamente.')
            return redirect('elecciones:panel_admin')
    else:
        form = MesaForm()
    return render(request, 'elecciones/form_generico.html', {'form': form, 'titulo': 'Agregar Mesa', 'icono': 'fa-layer-group'})

@login_required(login_url='/elecciones2026/')
def editar_mesa(request, mesa_id):
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    mesa = get_object_or_404(Mesa, id=mesa_id)
    if request.method == 'POST':
        form = MesaForm(request.POST, instance=mesa)
        if form.is_valid():
            form.save()
            messages.success(request, f'Mesa {mesa.numero_mesa} actualizada.')
            return redirect('elecciones:panel_admin')
    else:
        form = MesaForm(instance=mesa)
    return render(request, 'elecciones/form_generico.html', {'form': form, 'titulo': f'Editar Mesa {mesa.numero_mesa}', 'icono': 'fa-edit'})

@login_required(login_url='/elecciones2026/')
def eliminar_mesa(request, mesa_id):
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    mesa = get_object_or_404(Mesa, id=mesa_id)
    mesa.delete()
    messages.success(request, 'Mesa eliminada correctamente.')
    return redirect('elecciones:panel_admin')

@login_required(login_url='/elecciones2026/')
def crear_jurado(request):
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    if request.method == 'POST':
        form = JuradoForm(request.POST)
        if form.is_valid():
            cedula = form.cleaned_data['cedula']
            nombres = form.cleaned_data['nombres']
            mesa = form.cleaned_data['mesa']
            user, created = User.objects.get_or_create(username=cedula)
            if created:
                user.set_password(cedula)
                user.first_name = nombres
                user.save()
            mesa.responsable = user
            mesa.save()
            messages.success(request, 'Jurado asignado correctamente.')
            return redirect('elecciones:panel_admin')
    else:
        form = JuradoForm()
    return render(request, 'elecciones/form_generico.html', {'form': form, 'titulo': 'Asignar Jurado', 'icono': 'fa-user-check'})


# --- GESTIÓN DE PARTIDOS ---
@login_required(login_url='/elecciones2026/')
def crear_partido(request):
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    if request.method == 'POST':
        form = PartidoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Partido creado.')
            return redirect('elecciones:panel_admin')
    else:
        form = PartidoForm()
    return render(request, 'elecciones/form_generico.html', {'form': form, 'titulo': 'Agregar Partido', 'icono': 'fa-flag'})

@login_required(login_url='/elecciones2026/')
def editar_partido(request, partido_id):
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    partido = get_object_or_404(Partido, id=partido_id)
    if request.method == 'POST':
        form = PartidoForm(request.POST, request.FILES, instance=partido)
        if form.is_valid():
            form.save()
            messages.success(request, f'Partido {partido.siglas} actualizado.')
            return redirect('elecciones:panel_admin')
    else:
        form = PartidoForm(instance=partido)
    return render(request, 'elecciones/form_generico.html', {'form': form, 'titulo': f'Editar Partido: {partido.siglas}', 'icono': 'fa-edit'})

@login_required(login_url='/elecciones2026/')
def eliminar_partido(request, partido_id):
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    partido = get_object_or_404(Partido, id=partido_id)
    partido.delete()
    messages.success(request, 'Partido eliminado correctamente.')
    return redirect('elecciones:panel_admin')


# --- GESTIÓN DE CANDIDATOS ---
@login_required(login_url='/elecciones2026/')
def crear_candidato(request):
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    if request.method == 'POST':
        form = CandidatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidato creado.')
            return redirect('elecciones:panel_admin')
    else:
        form = CandidatoForm()
    return render(request, 'elecciones/form_generico.html', {'form': form, 'titulo': 'Agregar Candidato', 'icono': 'fa-user-tie'})

@login_required(login_url='/elecciones2026/')
def editar_candidato(request, candidato_id):
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    candidato = get_object_or_404(Candidato, id=candidato_id)
    if request.method == 'POST':
        form = CandidatoForm(request.POST, instance=candidato)
        if form.is_valid():
            form.save()
            messages.success(request, 'Candidato actualizado.')
            return redirect('elecciones:panel_admin')
    else:
        form = CandidatoForm(instance=candidato)
    return render(request, 'elecciones/form_generico.html', {'form': form, 'titulo': 'Editar Candidato', 'icono': 'fa-edit'})

@login_required(login_url='/elecciones2026/')
def eliminar_candidato(request, candidato_id):
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    candidato = get_object_or_404(Candidato, id=candidato_id)
    candidato.delete()
    messages.success(request, 'Candidato eliminado.')
    return redirect('elecciones:panel_admin')


# --- CARGAS AUTOMÁTICAS ---
@login_required(login_url='/elecciones2026/')
def cargar_tarjeton_camara_tolima(request):
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    camara, _ = Corporacion.objects.get_or_create(nombre='CAMARA')
    tarjeton_data = [
        {"nombre": "Partido Colombia Justa Libres", "siglas": "CJL", "color": "#1C3C6B", "numeros": [101, 102, 103, 104, 105, 106]},
        {"nombre": "Coalición U, MIRA, Salvación Nacional", "siglas": "COAL", "color": "#F39200", "numeros": [101, 102, 103, 104, 105, 106]},
        {"nombre": "Pacto Verde por el Tolima", "siglas": "PV", "color": "#00A859", "numeros": [101, 102, 103, 104, 105, 106]},
        {"nombre": "Partido Conservador Colombiano", "siglas": "C", "color": "#003893", "numeros": [101, 102, 103, 104, 105, 106]},
        {"nombre": "Partido Liberal Colombiano", "siglas": "L", "color": "#CE1126", "numeros": [101, 102, 103, 104, 105, 106]},
        {"nombre": "Partido Centro Democrático", "siglas": "CD", "color": "#2A82C6", "numeros": [101, 102, 103, 104, 105, 106]}
    ]
    for pd in tarjeton_data:
        partido, _ = Partido.objects.get_or_create(nombre=pd['nombre'], defaults={'siglas': pd['siglas'], 'logo_color': pd['color']})
        Candidato.objects.get_or_create(corporacion=camara, partido=partido, numero_tarjeton=None, defaults={'nombre': 'Voto al Logo'})
        for num in pd['numeros']:
            Candidato.objects.get_or_create(corporacion=camara, partido=partido, numero_tarjeton=num)
    messages.success(request, '¡Éxito! Tarjetón Cámara cargado.')
    return redirect('elecciones:panel_admin')

@login_required(login_url='/elecciones2026/')
def cargar_tarjeton_senado(request):
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    senado, _ = Corporacion.objects.get_or_create(nombre='SENADO')
    tarjeton_data = [
        {"nombre": "Pacto Histórico", "siglas": "PH", "color": "#E3007E", "numeros": [], "lista_cerrada": True},
        {"nombre": "Partido Conservador Colombiano", "siglas": "C", "color": "#003893", "numeros": list(range(1, 101)), "lista_cerrada": False},
        {"nombre": "Partido Liberal Colombiano", "siglas": "L", "color": "#CE1126", "numeros": list(range(1, 101)), "lista_cerrada": False},
        {"nombre": "Alianza Verde", "siglas": "VERDE", "color": "#00A859", "numeros": list(range(1, 101)), "lista_cerrada": False},
        {"nombre": "Partido Centro Democrático", "siglas": "CD", "color": "#2A82C6", "numeros": [], "lista_cerrada": True},
    ]
    for pd in tarjeton_data:
        partido, _ = Partido.objects.get_or_create(nombre=pd['nombre'], defaults={'siglas': pd['siglas'], 'logo_color': pd['color']})
        Candidato.objects.get_or_create(corporacion=senado, partido=partido, numero_tarjeton=None, defaults={'nombre': 'Voto a la Lista'})
        if not pd['lista_cerrada']:
            for num in pd['numeros']:
                Candidato.objects.get_or_create(corporacion=senado, partido=partido, numero_tarjeton=num)
    messages.success(request, '¡Éxito! Tarjetón Senado cargado.')
    return redirect('elecciones:panel_admin')

@login_required(login_url='/elecciones2026/')
def cargar_tarjeton_consulta(request):
    """
    MODIFICADO: Carga la estructura exacta de la imagen de referencia.
    Usamos el modelo 'Partido' para representar la 'Coalición/Consulta'
    """
    if not request.user.is_superuser: return redirect('elecciones:dashboard')
    consulta, _ = Corporacion.objects.get_or_create(nombre='CONSULTA')
    
    tarjeton_data = [
        {
            "nombre": "Consulta de las Soluciones: Salud, Seguridad y Educación", 
            "siglas": "SOLUCIONES", "color": "#F3B20B", 
            "candidatos": [
                "Claudia Nayibe Lopez Hernandez", 
                "Leonardo Humberto Huerta Gutierrez"
            ]
        },
        {
            "nombre": "La Gran Consulta por Colombia", 
            "siglas": "GRAN CONSULTA", "color": "#003893", 
            "candidatos": [
                "Mauricio Cardenas Santamaria",
                "David Andres Luna Sanchez",
                "Victoria Eugenia Davila Hoyos",
                "Juan Manuel Galan Pachon",
                "Paloma Susana Valencia Laserna",
                "Juan Carlos Pinzon Bueno",
                "Anibal Gaviria Correa",
                "Enrique Peñalosa Londoño",
                "Juan Daniel Oviedo Arango"
            ]
        },
        {
            "nombre": "Frente por la Vida", 
            "siglas": "FRENTE VIDA", "color": "#CE1126", 
            "candidatos": [
                "Hector Elias Pineda Salazar",
                "Edison Lucio Torres Moreno",
                "Roy Leonardo Barreras Montealegre",
                "Martha Viviana Bernal Amita",
                "Daniel Quintero Calle"
            ]
        }
    ]
    
    for pd in tarjeton_data:
        # Aquí el "Partido" actúa como la Gran Coalición
        partido, _ = Partido.objects.get_or_create(nombre=pd['nombre'], defaults={'siglas': pd['siglas'], 'logo_color': pd['color']})
        for idx, cand_name in enumerate(pd['candidatos'], start=1):
            # Guardamos el nombre real del candidato
            Candidato.objects.get_or_create(corporacion=consulta, partido=partido, numero_tarjeton=idx, defaults={'nombre': cand_name})
            
    messages.success(request, '¡Éxito! Tarjetón de Consultas cargado según el diseño de la Registraduría.')
    return redirect('elecciones:panel_admin')


# --- VISTAS DEL TARJETÓN Y E14 ---
@login_required(login_url='/elecciones2026/')
def digitar_votos(request):
    corp_nombre = request.GET.get('corp', 'CAMARA')
    corporacion, _ = Corporacion.objects.get_or_create(nombre=corp_nombre)

    if request.user.is_superuser:
        mesa_id = request.GET.get('mesa_id')
        if not mesa_id:
            messages.error(request, "Seleccione una mesa.")
            return redirect('elecciones:panel_admin')
        mesa_asignada = Mesa.objects.filter(id=mesa_id).first()
    else:
        mesa_asignada = Mesa.objects.filter(responsable=request.user).first()

    if not mesa_asignada:
        return render(request, 'elecciones/form_generico.html', {'titulo': 'Acceso Denegado', 'icono': 'fa-lock', 'form': None})

    candidatos_corp = list(Candidato.objects.filter(corporacion=corporacion).order_by('partido', 'numero_tarjeton'))

    if request.method == 'POST':
        ficha, created = FichaEscrutinio.objects.get_or_create(
            mesa=mesa_asignada, corporacion=corporacion,
            defaults={
                'usuario_registro': request.user,
                'votos_en_blanco': int(request.POST.get('votos_blancos') or 0),
                'votos_nulos': int(request.POST.get('votos_nulos') or 0),
                'votos_no_marcados': int(request.POST.get('votos_no_marcados') or 0),
            }
        )
        if not created:
            ficha.votos_en_blanco = int(request.POST.get('votos_blancos') or 0)
            ficha.votos_nulos = int(request.POST.get('votos_nulos') or 0)
            ficha.votos_no_marcados = int(request.POST.get('votos_no_marcados') or 0)
            ficha.usuario_registro = request.user
            ficha.save()

        total_votos_candidatos = 0
        for cand in candidatos_corp:
            votos = int(request.POST.get(f'votos_{cand.id}') or 0)
            total_votos_candidatos += votos
            DetalleVoto.objects.update_or_create(ficha=ficha, candidato=cand, defaults={'cantidad': votos})
            
        mesa_asignada.total_sufragantes = total_votos_candidatos + ficha.votos_en_blanco + ficha.votos_nulos + ficha.votos_no_marcados
        mesa_asignada.save()

        messages.success(request, f'¡Los votos de {corporacion.get_nombre_display()} han sido guardados!')
        if request.user.is_superuser:
            return redirect('elecciones:panel_admin')
        else:
            return redirect(f"/elecciones2026/jurado/tarjeton/?corp={corp_nombre}")

    ficha_existente = FichaEscrutinio.objects.filter(mesa=mesa_asignada, corporacion=corporacion).first()
    for cand in candidatos_corp:
        if ficha_existente:
            detalle = DetalleVoto.objects.filter(ficha=ficha_existente, candidato=cand).first()
            cand.votos_actuales = detalle.cantidad if detalle else 0
        else:
            cand.votos_actuales = 0

    votos_control = {
        'blancos': ficha_existente.votos_en_blanco if ficha_existente else 0,
        'nulos': ficha_existente.votos_nulos if ficha_existente else 0,
        'no_marcados': ficha_existente.votos_no_marcados if ficha_existente else 0,
    }

    context = {'mesa': mesa_asignada, 'candidatos': candidatos_corp, 'votos_control': votos_control, 'corporacion': corporacion}
    return render(request, 'elecciones/tarjeton.html', context)

@login_required(login_url='/elecciones2026/')
def ver_e14(request):
    corp_nombre = request.GET.get('corp', 'CAMARA')
    corporacion, _ = Corporacion.objects.get_or_create(nombre=corp_nombre)

    if request.user.is_superuser:
        mesa_id = request.GET.get('mesa_id')
        if not mesa_id:
            return redirect('elecciones:panel_admin')
        mesa_asignada = Mesa.objects.filter(id=mesa_id).first()
    else:
        mesa_asignada = Mesa.objects.filter(responsable=request.user).first()

    if not mesa_asignada:
        return render(request, 'elecciones/form_generico.html', {'titulo': 'Acceso Denegado', 'icono': 'fa-lock', 'form': None})

    candidatos_corp = list(Candidato.objects.filter(corporacion=corporacion).order_by('partido', 'numero_tarjeton'))

    if request.method == 'POST':
        ficha, created = FichaEscrutinio.objects.get_or_create(
            mesa=mesa_asignada, corporacion=corporacion,
            defaults={
                'usuario_registro': request.user,
                'votos_en_blanco': int(request.POST.get('votos_blancos') or 0),
                'votos_nulos': int(request.POST.get('votos_nulos') or 0),
                'votos_no_marcados': int(request.POST.get('votos_no_marcados') or 0),
            }
        )
        if not created:
            ficha.votos_en_blanco = int(request.POST.get('votos_blancos') or 0)
            ficha.votos_nulos = int(request.POST.get('votos_nulos') or 0)
            ficha.votos_no_marcados = int(request.POST.get('votos_no_marcados') or 0)
            ficha.usuario_registro = request.user
            ficha.save()

        total_votos_candidatos = 0
        for cand in candidatos_corp:
            votos = int(request.POST.get(f'votos_{cand.id}') or 0)
            total_votos_candidatos += votos
            DetalleVoto.objects.update_or_create(ficha=ficha, candidato=cand, defaults={'cantidad': votos})
            
        mesa_asignada.total_sufragantes = total_votos_candidatos + ficha.votos_en_blanco + ficha.votos_nulos + ficha.votos_no_marcados
        mesa_asignada.save()

        messages.success(request, f'¡Los resultados del E-14 Clásico ({corporacion.get_nombre_display()}) han sido guardados!')
        if request.user.is_superuser:
            return redirect('elecciones:panel_admin')
        else:
            return redirect(f"/elecciones2026/jurado/e14/?corp={corp_nombre}")

    ficha_existente = FichaEscrutinio.objects.filter(mesa=mesa_asignada, corporacion=corporacion).first()
    for cand in candidatos_corp:
        if ficha_existente:
            detalle = DetalleVoto.objects.filter(ficha=ficha_existente, candidato=cand).first()
            cand.votos_actuales = detalle.cantidad if detalle else ""
        else:
            cand.votos_actuales = ""

    votos_control = {
        'blancos': ficha_existente.votos_en_blanco if ficha_existente else "",
        'nulos': ficha_existente.votos_nulos if ficha_existente else "",
        'no_marcados': ficha_existente.votos_no_marcados if ficha_existente else "",
    }

    context = {'mesa': mesa_asignada, 'candidatos': candidatos_corp, 'votos_control': votos_control, 'corporacion': corporacion}
    return render(request, 'elecciones/e14.html', context)