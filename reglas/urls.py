from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReglaAutomaticaViewSet,
    EjecucionReglaViewSet,
    historial_reglas_view,
    exportar_historial_pdf,
    exportar_historial_excel,
)

router = DefaultRouter()
router.register('reglas', ReglaAutomaticaViewSet, basename='regla')
router.register('ejecuciones-reglas', EjecucionReglaViewSet, basename='ejecucion-regla')

urlpatterns = [
    path('', include(router.urls)),

    # Historial y exportación
    path('historial-reglas/', historial_reglas_view, name='historial-reglas'),
    path('historial-reglas/export/pdf/', exportar_historial_pdf, name='exportar-historial-pdf'),
    path('historial-reglas/export/excel/', exportar_historial_excel, name='exportar-historial-excel'),
]

"""
| Acción                     | Endpoint                                 | Método             |
| -------------------------- | ---------------------------------------- | ------------------ |
| Crear/Listar/Editar Regla  | `/reglas/reglas/`                        | GET/POST/PUT/PATCH |
| Activar/Desactivar Regla   | `/reglas/reglas/{id}/activar/`           | PATCH              |
| Ejecutar Regla Manualmente | `/reglas/reglas/ejecutar/`               | POST               |
| Listar ejecuciones         | `/reglas/ejecuciones-reglas/`            | GET                |
| Ver ejecución              | `/reglas/ejecuciones-reglas/{id}/`       | GET                |
| Registrar ejecución        | `/reglas/ejecuciones-reglas/`            | POST               |
| Historial filtrado         | `/reglas/historial-reglas/`              | GET                |
| Exportar a PDF             | `/reglas/historial-reglas/export/pdf/`   | GET                |
| Exportar a Excel           | `/reglas/historial-reglas/export/excel/` | GET                |

"""
