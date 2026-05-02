# notas/forms/observador_forms.py
from django import forms
from ..models import FichaEstudiante, RegistroObservador

class FichaEstudianteForm(forms.ModelForm):
    class Meta:
        model = FichaEstudiante
        exclude = ['estudiante']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lugar_nacimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'eps': forms.TextInput(attrs={'class': 'form-control'}),
            'grupo_sanguineo': forms.Select(attrs={'class': 'form-select'}),
            'enfermedades_alergias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nombre_padre': forms.TextInput(attrs={'class': 'form-control'}),
            'celular_padre': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_madre': forms.TextInput(attrs={'class': 'form-control'}),
            'celular_madre': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_acudiente': forms.TextInput(attrs={'class': 'form-control'}),
            'celular_acudiente': forms.TextInput(attrs={'class': 'form-control'}),
            'email_acudiente': forms.EmailInput(attrs={'class': 'form-control'}),
            'colegio_anterior': forms.TextInput(attrs={'class': 'form-control'}),
            'grado_anterior': forms.TextInput(attrs={'class': 'form-control'}),
            'espera_en_porteria': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'compromiso_padre': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'compromiso_estudiante': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
        }

class RegistroObservadorForm(forms.ModelForm):
    # CORRECCIÓN CRÍTICA: Definir subtipo como NO obligatorio para evitar bloqueos
    subtipo = forms.ChoiceField(
        choices=RegistroObservador.SUBTIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = RegistroObservador
        fields = ['fecha_suceso', 'tipo', 'subtipo', 'descripcion']
        widgets = {
            'fecha_suceso': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describa detalladamente el suceso...'}),
        }

class EstudianteCompromisoForm(forms.ModelForm):
    """
    Este es el formulario que causaba el ImportError. 
    Asegúrate de que este bloque esté completo al final del archivo.
    """
    compromiso_estudiante = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}), 
        label="Mi Compromiso para este año lectivo:", 
        help_text="Describe aquí tus metas y compromisos.", 
        required=False
    )
    class Meta:
        model = FichaEstudiante
        fields = ['compromiso_estudiante']