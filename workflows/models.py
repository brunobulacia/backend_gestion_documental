from django.db import models
from backend import settings

class FlujoTrabajo(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    tipo_documento = models.ForeignKey("documentos.TipoDocumento", on_delete=models.CASCADE, related_name="flujos")
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class ElementoFlujo(models.Model):
    TIPO_CHOICES = [
        ('INICIO', 'Evento de inicio'),
        ('FIN', 'Evento de fin'),
        ('TAREA', 'Tarea manual'),
        ('DECISION', 'Decisión si/no'),
    ]
    bpmnId = models.CharField(max_length=255, unique=True, default="")
    flujo = models.ForeignKey(FlujoTrabajo, on_delete=models.CASCADE, related_name="elementos")
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    orden = models.PositiveIntegerField()
    asignado_a_usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    asignado_a_rol = models.ForeignKey(
        "usuarios.Rol", null=True, blank=True, on_delete=models.SET_NULL
    )
    condicion = models.CharField(max_length=255, blank=True)  # para decisiones
    x = models.PositiveIntegerField(null=True, blank=True)
    y = models.PositiveIntegerField(null=True, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class TransicionFlujo(models.Model):
    origen = models.ForeignKey(ElementoFlujo, on_delete=models.CASCADE, related_name="transiciones_salida")
    destino = models.ForeignKey(ElementoFlujo, on_delete=models.CASCADE, related_name="transiciones_entrada")
    condicion = models.CharField(max_length=255, blank=True)  # para ramas si/no, por ejemplo
    bpmnId = models.CharField(max_length=255, unique=True, default="")
    def __str__(self):
        return f"{self.origen} → {self.destino}"

class Waypoint(models.Model):
    transicion = models.ForeignKey(TransicionFlujo, on_delete=models.CASCADE, related_name="waypoints")
    x = models.PositiveIntegerField(null=True, blank=True)
    y = models.PositiveIntegerField(null=True, blank=True)
