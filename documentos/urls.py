from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    descargar_version,
    documentos_view,
    historial_versiones,
    asignar_permiso,
    subir_nueva_version,
    crear_area,
    crear_tipo_documento,
    resumen_documentos,
    descargar_documento,
    listar_comentarios_version,
    crear_comentario,
    eliminar_comentario,
    DocumentoViewSet,
    agregar_metadatos,
    obtener_tipos_documentos,
)
from .views import buscar_documentos

router = DefaultRouter()
router.register(r'documentos', DocumentoViewSet, basename='documento')

urlpatterns = [
    path('', include(router.urls)),
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
    path('version/<uuid:version_id>/descargar/', descargar_documento, name='descargar-documento'),
    
    path("tipos/", crear_tipo_documento, name="crear-tipo"),
    path("areas/", crear_area, name="crear-area"),
    path("resumen/", resumen_documentos, name="resumen-documentos"),
    path("buscar/", buscar_documentos, name="buscar-documentos"),
    path("descargar/<int:version_id>/", descargar_version, name="descargar-version"),
    path('versiones/<uuid:version_id>/comentarios/', listar_comentarios_version),
    path('versiones/<uuid:version_id>/comentarios/crear/', crear_comentario),
    path('comentarios/<int:comentario_id>/eliminar/', eliminar_comentario),
    path('<uuid:documento_id>/agregar-metadatos/', agregar_metadatos, name='agregar-metadatos'),
    path('tipos-documentos/', obtener_tipos_documentos, name='obtener-tipos-documentos'),
]

urlpatterns += router.urls
