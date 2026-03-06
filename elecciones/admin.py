from django.contrib import admin
from .models import Corporacion, PuestoVotacion, Mesa, Partido, Candidato, FichaEscrutinio, DetalleVoto

@admin.register(PuestoVotacion)
class PuestoVotacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'municipio', 'departamento')
    list_filter = ('municipio',)

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero_mesa', 'puesto', 'responsable', 'total_sufragantes')
    list_filter = ('puesto',)

@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'siglas')

@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    list_display = ('partido', 'numero_tarjeton', 'corporacion', 'nombre')
    list_filter = ('corporacion', 'partido')

# Opcional: Para ver los votos rápido en el admin
class DetalleVotoInline(admin.TabularInline):
    model = DetalleVoto
    extra = 0

@admin.register(FichaEscrutinio)
class FichaEscrutinioAdmin(admin.ModelAdmin):
    list_display = ('mesa', 'corporacion', 'usuario_registro', 'esta_validada', 'fecha_registro')
    list_filter = ('corporacion', 'esta_validada')
    inlines = [DetalleVotoInline]

admin.site.register(Corporacion)