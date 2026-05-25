# notas/forms/observador_forms.py
from django import forms
from ..models import FichaEstudiante, RegistroObservador

class FichaEstudianteForm(forms.ModelForm):
    def clean_numero_documento(self):
        documento = self.cleaned_data.get('numero_documento')
        if not documento or str(documento).strip() == '':
            return None  # Permite nulos en BD para evitar errores de unicidad duplicada
        return documento

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
    # Añadimos un valor vacío '---' como opción válida para evitar que Django rechace las opciones vacías
    subtipo = forms.ChoiceField(
        choices=[('', '--- Seleccione Opción (Solo Comportamiento) ---')] + RegistroObservador.SUBTIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = RegistroObservador
        fields = ['fecha_suceso', 'tipo', 'subtipo', 'descripcion']
        widgets = {
            # Forzamos a Django a esperar formato de fecha estándar de navegadores modernos
            'fecha_suceso': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describa detalladamente el suceso...'}),
        }

class EstudianteCompromisoForm(forms.ModelForm):
    compromiso_estudiante = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}), 
        label="Mi Compromiso para este año lectivo:", 
        help_text="Describe aquí tus metas y a qué te comprometes para mejorar académicamente y como persona.", 
        required=False
    )
    class Meta:
        model = FichaEstudiante
        fields = ['compromiso_estudiante']