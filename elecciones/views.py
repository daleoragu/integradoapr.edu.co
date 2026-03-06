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

    total_mesas = Mesa.objects.count()
    fichas = FichaEscrutinio.objects.filter(corporacion__nombre='CAMARA')
    mesas_informadas = fichas.count()
    porcentaje_mesas = (mesas_informadas / total_mesas * 100) if total_mesas > 0 else 0

    votos_blancos = fichas.aggregate(Sum('votos_en_blanco'))['votos_en_blanco__sum'] or 0
    votos_nulos = fichas.aggregate(Sum('votos_nulos'))['votos_nulos__sum'] or 0
    votos_no_marcados = fichas.aggregate(Sum('votos_no_marcados'))['votos_no_marcados__sum'] or 0

    # --- NUEVA LÓGICA DE CÁLCULO ---
    resultados_partidos = []
    top_candidatos = []
    votos_validos_solo_candidatos = 0

    for partido in Partido.objects.all():
        votos_partido = 0
        candidatos_partido = []
        
        # Filtramos los candidatos que pertenecen a este partido en la Cámara
        candidatos_del_partido = Candidato.objects.filter(partido=partido, corporacion__nombre='CAMARA')
        
        if not candidatos_del_partido.exists():
            continue

        for cand in candidatos_del_partido:
            votos_cand = DetalleVoto.objects.filter(
                ficha__in=fichas,
                candidato=cand
            ).aggregate(Sum('cantidad'))['cantidad__sum'] or 0

            votos_partido += votos_cand
            
            candidatos_partido.append({
                'candidato': cand,
                'votos': votos_cand
            })
            
            top_candidatos.append({
                'candidato': cand,
                'partido': partido,
                'votos': votos_cand
            })

        votos_validos_solo_candidatos += votos_partido

        # Agregamos el partido solo si tiene candidatos
        resultados_partidos.append({
            'partido': partido,
            'votos': votos_partido,
            # Ordenamos los candidatos DENTRO del partido de mayor a menor
            'candidatos': sorted(candidatos_partido, key=lambda x: x['votos'], reverse=True)
        })

    # Ordenamos TODOS los partidos de mayor a menor
    resultados_partidos = sorted(resultados_partidos, key=lambda x: x['votos'], reverse=True)
    # Ordenamos TODOS los candidatos de mayor a menor para la vista general
    top_candidatos = sorted(top_candidatos, key=lambda x: x['votos'], reverse=True)
    
    votos_validos = votos_validos_solo_candidatos + votos_blancos

    # Cálculo de Porcentajes Globales para las barras
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
        'total_mesas': total_mesas,
        'mesas_informadas': mesas_informadas,
        'porcentaje_mesas': round(porcentaje_mesas, 2),
        'votos_validos': votos_validos,
        'votos_blancos': votos_blancos,
        'votos_nulos': votos_nulos,
        'votos_no_marcados': votos_no_marcados,
        'resultados_partidos': resultados_partidos,
        'top_candidatos': top_candidatos, # Nueva variable enviada al HTML
    }
    return render(request, 'elecciones/index.html', context)


def logout_jurado(request):
    logout(request)
    return redirect('elecciones:dashboard')

@login_required(login_url='/elecciones2026/')
def panel_admin(request):
    if not request.user.is_superuser:
        return redirect('elecciones:digitar_votos')
        
    if not Corporacion.objects.exists():
        Corporacion.objects.create(nombre='CAMARA')
        Corporacion.objects.create(nombre='SENADO')
        Corporacion.objects.create(nombre='CONSULTA')
        
    mesas = Mesa.objects.all().select_related('puesto', 'responsable').order_by('puesto', 'numero_mesa')
    partidos = Partido.objects.all()
    candidatos = Candidato.objects.all().select_related('partido', 'corporacion')
    
    return render(request, 'elecciones/panel_admin.html', {
        'mesas': mesas, 'partidos': partidos, 'candidatos': candidatos
    })

@login_required(login_url='/elecciones2026/')
def crear_puesto(request):
    if request.method == 'POST':
        form = PuestoVotacionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('elecciones:panel_admin')
    else:
        form = PuestoVotacionForm()
    return render(request, 'elecciones/form_generico.html', {'form': form, 'titulo': 'Agregar Puesto', 'icono': 'fa-school'})

@login_required(login_url='/elecciones2026/')
def crear_mesa(request):
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('elecciones:panel_admin')
    else:
        form = MesaForm()
    return render(request, 'elecciones/form_generico.html', {'form': form, 'titulo': 'Agregar Mesa', 'icono': 'fa-layer-group'})

@login_required(login_url='/elecciones2026/')
def crear_jurado(request):
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
            return redirect('elecciones:panel_admin')
    else:
        form = JuradoForm()
    return render(request, 'elecciones/form_generico.html', {'form': form, 'titulo': 'Asignar Jurado', 'icono': 'fa-user-check'})

@login_required(login_url='/elecciones2026/')
def crear_partido(request):
    if not request.user.is_superuser:
        return redirect('elecciones:digitar_votos')
    if request.method == 'POST':
        # AGREGAMOS request.FILES para aceptar la subida del logo
        form = PartidoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Partido agregado correctamente.')
            return redirect('elecciones:panel_admin')
    else:
        form = PartidoForm()
    return render(request, 'elecciones/form_generico.html', {'form': form, 'titulo': 'Agregar Partido', 'icono': 'fa-flag'})

@login_required(login_url='/elecciones2026/')
def editar_partido(request, partido_id):
    if not request.user.is_superuser:
        return redirect('elecciones:digitar_votos')
        
    partido = get_object_or_404(Partido, id=partido_id)
    
    if request.method == 'POST':
        # Pasamos instance=partido para que Django sepa que estamos actualizando
        form = PartidoForm(request.POST, request.FILES, instance=partido)
        if form.is_valid():
            form.save()
            messages.success(request, f'El partido {partido.nombre} fue actualizado.')
            return redirect('elecciones:panel_admin')
    else:
        # Cargamos el formulario con los datos actuales del partido
        form = PartidoForm(instance=partido)
        
    return render(request, 'elecciones/form_generico.html', {'form': form, 'titulo': f'Editar Partido: {partido.siglas}', 'icono': 'fa-edit'})

@login_required(login_url='/elecciones2026/')
def crear_candidato(request):
    if not request.user.is_superuser:
        return redirect('elecciones:digitar_votos')
    if request.method == 'POST':
        form = CandidatoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('elecciones:panel_admin')
    else:
        form = CandidatoForm()
    return render(request, 'elecciones/form_generico.html', {'form': form, 'titulo': 'Agregar Candidato', 'icono': 'fa-user-tie'})

@login_required(login_url='/elecciones2026/')
def cargar_tarjeton_camara_tolima(request):
    if not request.user.is_superuser:
        return redirect('elecciones:dashboard')

    camara, _ = Corporacion.objects.get_or_create(nombre='CAMARA')
    tarjeton_data = [
        {"nombre": "Partido Colombia Justa Libres", "siglas": "CJL", "color": "#1C3C6B", "numeros": [101, 102, 103, 104, 105, 106]},
        {"nombre": "Coalición U, MIRA, Salvación Nacional, ADA", "siglas": "COAL", "color": "#F39200", "numeros": [101, 102, 103, 104, 105, 106]},
        {"nombre": "Pacto Verde por el Tolima", "siglas": "PV", "color": "#00A859", "numeros": [101, 102, 103, 104, 105, 106]},
        {"nombre": "Partido Conservador Colombiano", "siglas": "C", "color": "#003893", "numeros": [101, 102, 103, 104, 105, 106]},
        {"nombre": "Partido Liberal Colombiano", "siglas": "L", "color": "#CE1126", "numeros": [101, 102, 103, 104, 105, 106]},
        {"nombre": "Partido Político La Fuerza de la Paz", "siglas": "FDP", "color": "#5D2C81", "numeros": [101, 102, 104, 105, 106]},
        {"nombre": "Partido Político Dignidad & Compromiso", "siglas": "D&C", "color": "#3B1B54", "numeros": [101, 102, 103, 104, 105]},
        {"nombre": "Fuerza Tolima", "siglas": "FT", "color": "#F08200", "numeros": [101, 102, 106]},
        {"nombre": "Partido Centro Democrático", "siglas": "CD", "color": "#2A82C6", "numeros": [101, 102, 103, 104, 105, 106]}
    ]
    for pd in tarjeton_data:
        partido, _ = Partido.objects.get_or_create(nombre=pd['nombre'], defaults={'siglas': pd['siglas'], 'logo_color': pd['color']})
        Candidato.objects.get_or_create(corporacion=camara, partido=partido, numero_tarjeton=None, defaults={'nombre': 'Voto al Logo'})
        for num in pd['numeros']:
            Candidato.objects.get_or_create(corporacion=camara, partido=partido, numero_tarjeton=num)

    messages.success(request, '¡Éxito! Tarjetón cargado en el sistema.')
    return redirect('elecciones:panel_admin')


# --- VISTA 1: EL TARJETÓN TÁCTIL (INTERACTIVO) ---
@login_required(login_url='/elecciones2026/')
def digitar_votos(request):
    if request.user.is_superuser:
        mesa_id = request.GET.get('mesa_id')
        if not mesa_id:
            messages.error(request, "Seleccione una mesa para ingresar votos.")
            return redirect('elecciones:panel_admin')
        mesa_asignada = Mesa.objects.filter(id=mesa_id).first()
    else:
        mesa_asignada = Mesa.objects.filter(responsable=request.user).first()

    if not mesa_asignada:
        return render(request, 'elecciones/form_generico.html', {'titulo': 'Acceso Denegado', 'icono': 'fa-lock', 'form': None})

    camara = Corporacion.objects.filter(nombre='CAMARA').first()
    candidatos_camara = list(Candidato.objects.filter(corporacion=camara).order_by('partido', 'numero_tarjeton'))

    if request.method == 'POST':
        ficha, created = FichaEscrutinio.objects.get_or_create(
            mesa=mesa_asignada, corporacion=camara,
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
        for cand in candidatos_camara:
            votos = int(request.POST.get(f'votos_{cand.id}') or 0)
            total_votos_candidatos += votos
            DetalleVoto.objects.update_or_create(
                ficha=ficha, candidato=cand, defaults={'cantidad': votos}
            )
            
        mesa_asignada.total_sufragantes = total_votos_candidatos + ficha.votos_en_blanco + ficha.votos_nulos + ficha.votos_no_marcados
        mesa_asignada.save()

        messages.success(request, f'¡Los votos han sido guardados desde el Tarjetón!')
        if request.user.is_superuser:
            return redirect('elecciones:panel_admin')
        else:
            return redirect('elecciones:digitar_votos')

    ficha_existente = FichaEscrutinio.objects.filter(mesa=mesa_asignada, corporacion=camara).first()
    for cand in candidatos_camara:
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

    context = {'mesa': mesa_asignada, 'candidatos': candidatos_camara, 'votos_control': votos_control}
    return render(request, 'elecciones/tarjeton.html', context)


# --- VISTA 2: EL FORMATO E-14 (TABLA FÍSICA CLÁSICA) ---
@login_required(login_url='/elecciones2026/')
def ver_e14(request):
    if request.user.is_superuser:
        mesa_id = request.GET.get('mesa_id')
        if not mesa_id:
            messages.error(request, "Seleccione una mesa para ver su E-14.")
            return redirect('elecciones:panel_admin')
        mesa_asignada = Mesa.objects.filter(id=mesa_id).first()
    else:
        mesa_asignada = Mesa.objects.filter(responsable=request.user).first()

    if not mesa_asignada:
        return render(request, 'elecciones/form_generico.html', {'titulo': 'Acceso Denegado', 'icono': 'fa-lock', 'form': None})

    camara = Corporacion.objects.filter(nombre='CAMARA').first()
    candidatos_camara = list(Candidato.objects.filter(corporacion=camara).order_by('partido', 'numero_tarjeton'))

    if request.method == 'POST':
        ficha, created = FichaEscrutinio.objects.get_or_create(
            mesa=mesa_asignada, corporacion=camara,
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
        for cand in candidatos_camara:
            votos = int(request.POST.get(f'votos_{cand.id}') or 0)
            total_votos_candidatos += votos
            DetalleVoto.objects.update_or_create(
                ficha=ficha, candidato=cand, defaults={'cantidad': votos}
            )
            
        mesa_asignada.total_sufragantes = total_votos_candidatos + ficha.votos_en_blanco + ficha.votos_nulos + ficha.votos_no_marcados
        mesa_asignada.save()

        messages.success(request, f'¡Los resultados del E-14 Clásico han sido guardados!')
        if request.user.is_superuser:
            return redirect('elecciones:panel_admin')
        else:
            return redirect('elecciones:ver_e14')

    ficha_existente = FichaEscrutinio.objects.filter(mesa=mesa_asignada, corporacion=camara).first()
    for cand in candidatos_camara:
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

    context = {'mesa': mesa_asignada, 'candidatos': candidatos_camara, 'votos_control': votos_control}
    return render(request, 'elecciones/e14.html', context)