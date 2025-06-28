# notas/forms.py

from django import forms
from django.contrib.auth.models import User, Group
# Se importan todos los modelos necesarios
from .models import (
    Mensaje, Estudiante, Docente, FichaEstudiante, RegistroObservador, 
    Curso, Materia, AreaConocimiento, ImagenCarrusel
)
from .models.portal_models import DocumentoPublico, FotoGaleria, Noticia

# ===============================================================
# FORMULARIOS PARA LA GESTIÓN DEL PORTAL PÚBLICO
# ===============================================================

class DocumentoPublicoForm(forms.ModelForm):
    class Meta:
        model = DocumentoPublico
        fields = ['titulo', 'descripcion', 'archivo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class FotoGaleriaForm(forms.ModelForm):
    class Meta:
        model = FotoGaleria
        fields = ['titulo', 'imagen']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = ['titulo', 'resumen', 'cuerpo', 'imagen_portada', 'estado'] # Se añade 'estado'
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'resumen': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cuerpo': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'imagen_portada': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}), # Se le da estilo al campo 'estado'
        }

class ImagenCarruselForm(forms.ModelForm):
    class Meta:
        model = ImagenCarrusel
        fields = ['titulo', 'subtitulo', 'imagen', 'orden', 'visible']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'subtitulo': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control'}),
            'visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ===============================================================
# FORMULARIO PARA MENSAJERÍA (CofraMail)
# ===============================================================

class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        nombre_completo = obj.get_full_name() or obj.username
        try:
            if hasattr(obj, 'estudiante'):
                rol = f"(Estudiante - {obj.estudiante.curso.nombre})"
            elif hasattr(obj, 'docente'):
                rol = "(Docente)"
            else:
                rol = "(Admin)" if obj.is_staff else ""
        except:
            rol = "(Estudiante)" if hasattr(obj, 'estudiante') else ""
        return f"{nombre_completo} {rol}".strip()


class MensajeForm(forms.ModelForm):
    destinatario = UserChoiceField(queryset=User.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}), label="Para:")
    asunto = forms.CharField(label="Asunto:", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Mensaje
        fields = ['destinatario', 'asunto', 'cuerpo']
        widgets = {'cuerpo': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),}
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(MensajeForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['destinatario'].queryset = User.objects.exclude(pk=user.pk).order_by('first_name', 'last_name')


# ===============================================================
# FORMULARIOS PARA EL OBSERVADOR DEL ESTUDIANTE
# ===============================================================

class FichaEstudianteForm(forms.ModelForm):
    class Meta:
        model = FichaEstudiante
        exclude = ['estudiante']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lugar_nacimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'eps': forms.TextInput(attrs={'class': 'form-control'}),
            'grupo_sanguineo': forms.TextInput(attrs={'class': 'form-control'}),
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
        }

class RegistroObservadorForm(forms.ModelForm):
    class Meta:
        model = RegistroObservador
        fields = ['fecha_suceso', 'tipo', 'subtipo', 'descripcion']
        widgets = {
            'fecha_suceso': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'subtipo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describa detalladamente el suceso...'}),
        }

class EstudianteCompromisoForm(forms.ModelForm):
    compromiso_estudiante = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}), label="Mi Compromiso para este año lectivo:", help_text="Describe aquí tus metas y a qué te comprometes para mejorar académicamente y como persona.", required=False)
    class Meta:
        model = FichaEstudiante
        fields = ['compromiso_estudiante']

# ===============================================================
# FORMULARIOS PARA LA GESTIÓN DE ESTUDIANTES (CRUD)
# ===============================================================

class AdminCrearEstudianteForm(forms.Form):
    nombres = forms.CharField(label="Nombres Completos", max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    apellidos = forms.CharField(label="Apellidos Completos", max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    tipo_documento = forms.ChoiceField(label="Tipo de Documento", choices=FichaEstudiante.TIPO_DOCUMENTO_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    numero_documento = forms.CharField(label="Número de Documento", max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Este será el usuario y contraseña inicial'}))
    curso = forms.ModelChoiceField(label="Asignar al Curso", queryset=Curso.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))

    def clean_nombres(self):
        return self.cleaned_data.get('nombres', '').upper()

    def clean_apellidos(self):
        return self.cleaned_data.get('apellidos', '').upper()

    def clean_numero_documento(self):
        numero = self.cleaned_data.get('numero_documento')
        if User.objects.filter(username=numero).exists():
            raise forms.ValidationError("Ya existe un usuario con este número de documento.")
        return numero

class AdminEditarEstudianteForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombres", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Apellidos", widget=forms.TextInput(attrs={'class': 'form-control'}))
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(), label="Curso", widget=forms.Select(attrs={'class': 'form-select'}))
    is_active = forms.BooleanField(required=False, label="¿Estudiante Activo?", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    class Meta:
        model = FichaEstudiante
        fields = '__all__'
        exclude = ['estudiante']
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'grupo_sanguineo': forms.Select(attrs={'class': 'form-select'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'lugar_nacimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'eps': forms.TextInput(attrs={'class': 'form-control'}),
            'enfermedades_alergias': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
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
            'compromiso_padre': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'compromiso_estudiante': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def clean_first_name(self):
        return self.cleaned_data.get('first_name', '').upper()

    def clean_last_name(self):
        return self.cleaned_data.get('last_name', '').upper()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            estudiante_profile = self.instance.estudiante
            self.fields['first_name'].initial = estudiante_profile.user.first_name
            self.fields['last_name'].initial = estudiante_profile.user.last_name
            self.fields['curso'].initial = estudiante_profile.curso
            self.fields['is_active'].initial = estudiante_profile.is_active

    def save(self, commit=True):
        ficha = super().save(commit=False)
        estudiante_profile = ficha.estudiante
        user = estudiante_profile.user
        
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        estudiante_profile.curso = self.cleaned_data['curso']
        estudiante_profile.is_active = self.cleaned_data['is_active']
        ficha.tipo_documento = self.cleaned_data['tipo_documento']

        if commit:
            user.save()
            estudiante_profile.save()
            ficha.save()
            
        return ficha

# ===============================================================
# FORMULARIOS PARA GESTIÓN ACADÉMICA
# ===============================================================

class AreaConocimientoForm(forms.ModelForm):
    """
    Formulario para crear y editar Áreas de Conocimiento.
    """
    class Meta:
        model = AreaConocimiento
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: CIENCIAS NATURALES Y EDUCACIÓN AMBIENTAL'})
        }
    
    def clean_nombre(self):
        return self.cleaned_data.get('nombre', '').upper()

class MateriaForm(forms.ModelForm):
    """
    Formulario para crear y editar Materias (sin I.H.).
    """
    class Meta:
        model = Materia
        # --- CORRECCIÓN: SE ELIMINA 'intensidad_horaria' DE LA LISTA ---
        fields = ['nombre', 'abreviatura', 'area']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: CIENCIAS SOCIALES'}),
            'abreviatura': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: C. SOC'}),
            'area': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['area'].queryset = AreaConocimiento.objects.order_by('nombre')
        self.fields['abreviatura'].required = False

    def clean_nombre(self):
        return self.cleaned_data.get('nombre', '').upper()
    
    def clean_abreviatura(self):
        abreviatura = self.cleaned_data.get('abreviatura')
        if abreviatura:
            return abreviatura.upper()
        return None
