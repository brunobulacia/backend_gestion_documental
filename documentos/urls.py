from django.urls import path

from .views import (
    descargar_version,
    documentos_view,
    historial_versiones,
    asignar_permiso,
    subir_nueva_version,
    crear_area,
    crear_tipo_documento,
    resumen_documentos,
)
from .views import buscar_documentos

urlpatterns = [
    path("", documentos_view, name="documentos_view"),
    path(
        "<uuid:documento_id>/versiones/",
        historial_versiones,
        name="historial-versiones",
    ),
    path(
        "<uuid:documento_id>/permisos/",
        asignar_permiso,
        name="asignar-permiso",
    ),
    path(
        "<uuid:documento_id>/nueva-version/",
        subir_nueva_version,
        name="subir-nueva-version",
    ),
    path("tipos/", crear_tipo_documento, name="crear-tipo"),
    path("areas/", crear_area, name="crear-area"),
    path("resumen/", resumen_documentos, name="resumen-documentos"),
    path("buscar/", buscar_documentos, name="buscar-documentos"),
    path("descargar/<int:version_id>/", descargar_version, name="descargar-version"),
]
