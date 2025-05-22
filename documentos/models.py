import uuid
import os
from django.db import models
from django.conf import settings


class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Area(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Documento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    tipo = models.ForeignKey(TipoDocumento, on_delete=models.SET_NULL, null=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documentos_creados",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    es_publico = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo


def ruta_documento_personalizada(instance, filename):
    area = instance.documento.area.nombre if instance.documento.area else "sin_area"
    tipo = instance.documento.tipo.nombre if instance.documento.tipo else "sin_tipo"

    area = area.replace(" ", "_").lower()
    tipo = tipo.replace(" ", "_").lower()
    return os.path.join("documentos", area, tipo, filename)


class DocumentoVersion(models.Model):
    documento = models.ForeignKey(
        Documento, on_delete=models.CASCADE, related_name="versiones"
    )
    archivo = models.FileField(upload_to=ruta_documento_personalizada)
    version = models.PositiveIntegerField()
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("documento", "version")
        ordering = ["-version"]

    def __str__(self):
        return f"{self.documento.titulo} - v{self.version}"


class ComentarioDocumento(models.Model):
    version = models.ForeignKey(
        DocumentoVersion, on_delete=models.CASCADE, related_name="comentarios"
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    es_publico = models.BooleanField(default=False)
    rol = models.ForeignKey('usuarios.Rol', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Comentario de {self.autor} en {self.version}"


class MetadatoPersonalizado(models.Model):
    documento = models.ForeignKey(
        Documento, on_delete=models.CASCADE, related_name="metadatos"
    )
    clave = models.CharField(max_length=100)
    valor = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.clave}: {self.valor}"


class PermisoDocumento(models.Model):
    documento = models.ForeignKey(
        Documento, on_delete=models.CASCADE, related_name="permisos"
    )
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    puede_ver = models.BooleanField(default=True)
    puede_editar = models.BooleanField(default=False)
    puede_comentar = models.BooleanField(default=False)
    class Meta:
        unique_together = ("documento", "usuario")
