from django.urls import path
from .views import documentos_view, historial_versiones, asignar_permiso, subir_nueva_version

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
]
