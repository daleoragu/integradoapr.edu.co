# notas/forms/observador_forms.py

from django import forms
from django.utils.safestring import mark_safe
from ..models.comunicaciones import RegistroObservador
from ..models.perfiles import FichaEstudiante

class RegistroObservadorForm(forms.ModelForm):
    class Meta:
        model = RegistroObservador
        fields = ['fecha_suceso', 'tipo', 'subtipo', 'descripcion']
        widgets = {
            'fecha_suceso': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'subtipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control', 
                    'rows': 6,
                    'placeholder': 'Describa detalladamente el suceso observado...'
                }
            ),
        }
        labels = {
            'fecha_suceso': 'Fecha del Suceso',
            'tipo': 'Tipo de Observación',
            'subtipo': 'Naturaleza (solo para Comportamental)',
            'descripcion': 'Descripción Detallada',
        }

# --- Widget personalizado para previsualizar la imagen ---
class ImagePreviewWidget(forms.widgets.FileInput):
    def render(self, name, value, attrs=None, **kwargs):
        input_html = super().render(name, value, attrs, **kwargs)
        img_html = ''
        if value and hasattr(value, 'url'):
            img_html = f'<img src="{value.url}" alt="Foto actual" style="max-height: 150px; margin-top: 10px; border-radius: 8px;">'
        return mark_safe(f'{img_html}<br>{input_html}')


class FichaEstudianteForm(forms.ModelForm):
    # Definimos explícitamente el campo de la foto para usar nuestro widget personalizado
    foto = forms.ImageField(
        required=False, 
        widget=ImagePreviewWidget,
        help_text="Cargue una nueva foto para reemplazar la actual. Dejar en blanco para conservarla."
    )

    class Meta:
        model = FichaEstudiante
        # Incluimos 'foto' en la lista de campos
        fields = [
            'foto', 'lugar_nacimiento', 'fecha_nacimiento', 'eps', 'grupo_sanguineo',
            'enfermedades_alergias', 'nombre_padre', 'celular_padre', 'nombre_madre',
            'celular_madre', 'nombre_acudiente', 'celular_acudiente', 'email_acudiente',
            'espera_en_porteria', 'colegio_anterior', 'grado_anterior', 'compromiso_padre',
            'compromiso_estudiante'
        ]
        
        widgets = {
            'lugar_nacimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'eps': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la EPS'}),
            'grupo_sanguineo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: O+'}),
            'enfermedades_alergias': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nombre_padre': forms.TextInput(attrs={'class': 'form-control'}),
            'celular_padre': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_madre': forms.TextInput(attrs={'class': 'form-control'}),
            'celular_madre': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_acudiente': forms.TextInput(attrs={'class': 'form-control'}),
            'celular_acudiente': forms.TextInput(attrs={'class': 'form-control'}),
            'email_acudiente': forms.EmailInput(attrs={'class': 'form-control'}),
            'espera_en_porteria': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'colegio_anterior': forms.TextInput(attrs={'class': 'form-control'}),
            'grado_anterior': forms.TextInput(attrs={'class': 'form-control'}),
            'compromiso_padre': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'compromiso_estudiante': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
