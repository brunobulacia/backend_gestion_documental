from django.urls import path
from . import views

urlpatterns = [
    path('flujos/', views.flujo_trabajo_list_create),
    path('flujos/<int:pk>/', views.flujo_trabajo_detail),
    path('flujos/<int:flujo_id>/validar/', views.validar_flujo),
    path('flujos/<int:flujo_id>/asociar/', views.asociar_flujo_tipo_documento),
    path('flujos/<int:flujo_id>/json/', views.obtener_flujo_json),

    path('elementos/', views.crear_elemento_flujo),
    path('elementos/<int:pk>/', views.actualizar_eliminar_elemento),

    path('transiciones/', views.crear_transicion),
    path('transiciones/<int:pk>/', views.actualizar_eliminar_transicion),
]  