from django.db import models
from django.contrib.auth.models import User
from documentos.models import Documento
from django.conf import settings


class Formulario(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    tipo_documento = models.ForeignKey('documentos.TipoDocumento', on_delete=models.CASCADE)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="formulario_creados"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class CampoFormulario(models.Model):
    TIPO_CHOICES = [
        ('text', 'Texto'),
        ('number', 'Número'),
        ('date', 'Fecha'),
        ('select', 'Lista Desplegable'),
        ('checkbox', 'Checkbox'),
    ]

    formulario = models.ForeignKey(Formulario, related_name='campos', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    opciones = models.TextField(blank=True, help_text="Opciones separadas por coma (solo para listas)")
    obligatorio = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class RespuestaFormulario(models.Model):
    formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE)
    documento = models.ForeignKey(Documento, on_delete=models.CASCADE)
    completado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="formulario_repondido"
    )
    fecha_respuesta = models.DateTimeField(auto_now_add=True)
    datos = models.JSONField()

    def __str__(self):
        return f"Respuesta a {self.formulario.nombre} por {self.completado_por.username}"
