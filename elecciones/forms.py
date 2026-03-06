from django import forms
from django.contrib.auth.models import User
from .models import PuestoVotacion, Mesa, FichaEscrutinio, DetalleVoto, Partido, Candidato

TAILWIND_INPUT_CLASS = 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-[#003893] focus:ring-[#003893] sm:text-sm p-2 border'

class PuestoVotacionForm(forms.ModelForm):
    class Meta:
        model = PuestoVotacion
        fields = ['nombre', 'direccion']
        labels = {
            'nombre': 'Nombre del Puesto (Ej: Colegio Santander)',
            'direccion': 'Dirección (Opcional)'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'I.E.T. Alfonso Palacio Rudas'}),
            'direccion': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Cra 12 # 34-56'}),
        }

class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ['puesto', 'numero_mesa']
        labels = {
            'puesto': 'Seleccione el Puesto de Votación',
            'numero_mesa': 'Número de la Mesa'
        }
        widgets = {
            'puesto': forms.Select(attrs={'class': TAILWIND_INPUT_CLASS}),
            'numero_mesa': forms.NumberInput(attrs={'class': TAILWIND_INPUT_CLASS, 'min': '1', 'placeholder': 'Ej: 1, 2, 3...'}),
        }

class JuradoForm(forms.Form):
    nombres = forms.CharField(max_length=150, label="Nombre Completo del Jurado", widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Ej: Juan Pérez'}))
    cedula = forms.CharField(max_length=20, label="Número de Cédula (Será su usuario y contraseña)", widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Ej: 100200300'}))
    mesa = forms.ModelChoiceField(queryset=Mesa.objects.all(), label="Asignar a la Mesa", widget=forms.Select(attrs={'class': TAILWIND_INPUT_CLASS}))

# --- FORMULARIOS PARA PARTIDOS Y CANDIDATOS ---
class PartidoForm(forms.ModelForm):
    class Meta:
        model = Partido
        fields = ['nombre', 'siglas', 'logo_color', 'logo'] # SE AGREGÓ 'logo'
        labels = {
            'nombre': 'Nombre del Partido Político',
            'siglas': 'Siglas o Letra (Ej: L, C, PV)',
            'logo_color': 'Color Representativo de Fondo',
            'logo': 'Imagen/Logo del Partido (Recomendado PNG transparente)'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Ej: Partido Liberal Colombiano'}),
            'siglas': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Ej: L'}),
            'logo_color': forms.TextInput(attrs={'type': 'color', 'class': 'mt-1 block h-10 w-full rounded-md border-gray-300 shadow-sm cursor-pointer'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-[#003893] file:text-white hover:file:bg-blue-800 cursor-pointer'}),
        }

class CandidatoForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = ['corporacion', 'partido', 'numero_tarjeton', 'nombre']
        labels = {
            'corporacion': 'Tipo de Elección (Cámara, Senado, etc.)',
            'partido': 'Partido Político',
            'numero_tarjeton': 'Número en el Tarjetón',
            'nombre': 'Nombre del Candidato (Opcional)'
        }
        widgets = {
            'corporacion': forms.Select(attrs={'class': TAILWIND_INPUT_CLASS}),
            'partido': forms.Select(attrs={'class': TAILWIND_INPUT_CLASS}),
            'numero_tarjeton': forms.NumberInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Ej: 101'}),
            'nombre': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Ej: Juan Pérez (Opcional)'}),
        }