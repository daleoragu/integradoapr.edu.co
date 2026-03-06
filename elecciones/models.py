from django.db import models
from django.contrib.auth.models import User

# Opciones fijas para el tipo de elección
TIPO_ELECCION_CHOICES = [
    ('CAMARA', 'Cámara de Representantes'),
    ('SENADO', 'Senado de la República'),
    ('CONSULTA', 'Consulta Presidencial'),
]

class Corporacion(models.Model):
    nombre = models.CharField(max_length=20, choices=TIPO_ELECCION_CHOICES)
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return self.get_nombre_display()

class PuestoVotacion(models.Model):
    nombre = models.CharField(max_length=200) # Ej: "Colegio Alfonso Palacio Rudas"
    departamento = models.CharField(max_length=100, default='Tolima')
    municipio = models.CharField(max_length=100, default='Honda')
    direccion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.municipio})"

class Mesa(models.Model):
    puesto = models.ForeignKey(PuestoVotacion, on_delete=models.CASCADE, related_name='mesas')
    numero_mesa = models.IntegerField()
    # El usuario responsable de registrar los datos de esta mesa
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Datos de control para validar el E-14
    total_sufragantes = models.IntegerField(default=0, help_text="Total de personas que votaron según formulario E-11")

    class Meta:
        unique_together = ('puesto', 'numero_mesa')
        ordering = ['puesto', 'numero_mesa']

    def __str__(self):
        return f"Mesa {self.numero_mesa} - {self.puesto.nombre}"

class Partido(models.Model):
    nombre = models.CharField(max_length=150)
    siglas = models.CharField(max_length=10, blank=True)
    logo_color = models.CharField(max_length=20, default="#cccccc", help_text="Color HEX para las gráficas")
    
    # NUEVO CAMPO: Para subir la imagen del logo
    logo = models.ImageField(upload_to='logos_partidos/', null=True, blank=True, help_text="Sube el logo oficial del partido (Opcional)")
    
    def __str__(self):
        return self.nombre

class Candidato(models.Model):
    corporacion = models.ForeignKey(Corporacion, on_delete=models.CASCADE)
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    numero_tarjeton = models.IntegerField(null=True, blank=True, help_text="Dejar en blanco si es voto 'Solo por el partido' o lista cerrada")
    nombre = models.CharField(max_length=200, blank=True, help_text="Opcional. Para cámara/senado suele bastar con el número")
    
    class Meta:
        ordering = ['partido', 'numero_tarjeton']

    def __str__(self):
        if self.numero_tarjeton:
            return f"{self.partido.nombre} - {self.numero_tarjeton}"
        return f"{self.partido.nombre} (Voto al Partido/Lista)"

class FichaEscrutinio(models.Model):
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    corporacion = models.ForeignKey(Corporacion, on_delete=models.CASCADE)
    
    # Totales de control de la mesa para esta corporación específica
    votos_en_blanco = models.IntegerField(default=0)
    votos_nulos = models.IntegerField(default=0)
    votos_no_marcados = models.IntegerField(default=0)
    
    # Metadatos de auditoría
    usuario_registro = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    esta_validada = models.BooleanField(default=False, help_text="True si el SuperAdmin ya revisó que no hay descuadres")

    class Meta:
        # Una mesa solo puede tener UNA ficha de Cámara, UNA de Senado, etc.
        unique_together = ('mesa', 'corporacion')

    def __str__(self):
        return f"Escrutinio {self.corporacion} - {self.mesa}"

class DetalleVoto(models.Model):
    ficha = models.ForeignKey(FichaEscrutinio, on_delete=models.CASCADE, related_name='votos_detalle')
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=0)

    class Meta:
        unique_together = ('ficha', 'candidato')

    def __str__(self):
        return f"{self.cantidad} votos para {self.candidato} en {self.ficha.mesa}"