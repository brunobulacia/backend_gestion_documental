from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FormularioViewSet, CampoFormularioViewSet, RespuestaFormularioViewSet

router = DefaultRouter()
router.register('formularios', FormularioViewSet, basename='formulario')
router.register('campos-formulario', CampoFormularioViewSet, basename='campo-formulario')
router.register('respuestas-formulario', RespuestaFormularioViewSet, basename='respuesta-formulario')

urlpatterns = [
    path('campos-formulario/id_form=<int:id_form>/', CampoFormularioViewSet.as_view({'get': 'list_by_formulario'})),
    path('', include(router.urls)),
]


"""
| Método   | URL                                   | Descripción                      |
| -------- | ------------------------------------- | -------------------------------- |
| `GET`    | `/formularios/formularios/`           | Listar formularios               |
| `POST`   | `/formularios/formularios/`           | Crear formulario                 |
| `GET`    | `/formularios/formularios/{id}/`      | Ver un formulario                |
| `PUT`    | `/formularios/formularios/{id}/`      | Editar formulario                |
| `DELETE` | `/formularios/formularios/{id}/`      | Eliminar formulario              |
| `POST`   | `/formularios/campos-formulario/`     | Agregar campo a un formulario    |
| `POST`   | `/formularios/respuestas-formulario/` | Completar (responder) formulario |
"""