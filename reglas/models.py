from django.db import models
from django.conf import settings


class ReglaAutomatica(models.Model):
    EVENTOS = [
        ('formulario_completado', 'Formulario completado'),
        ('documento_cargado', 'Documento cargado'),
        ('estado_actualizado', 'Cambio de estado'),
    ]

    ACCIONES = [
        ('notificar', 'Enviar notificación'),
        ('cambiar_estado', 'Actualizar estado del documento'),
        ('activar_workflow', 'Activar flujo de trabajo'),
        ('actualizar_campo', 'Actualizar campo del documento'),
    ]

    nombre = models.CharField(max_length=255)
    evento = models.CharField(max_length=50, choices=EVENTOS)
    condicion = models.JSONField(help_text="Ej: {'tipo_documento': 'contrato'}")
    accion = models.CharField(max_length=50, choices=ACCIONES)
    parametros_accion = models.JSONField(help_text="Ej: {'nuevo_estado': 'validado'}")
    activa = models.BooleanField(default=True)
    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documentos_creados",)
    creada_en = models.DateTimeField(auto_now_add=True)


class EjecucionRegla(models.Model):
    regla = models.ForeignKey(ReglaAutomatica, on_delete=models.CASCADE)
    evento = models.CharField(max_length=50)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documentos_creados",)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=[('exito', 'Éxito'), ('error', 'Error')])
    mensaje = models.TextField()
