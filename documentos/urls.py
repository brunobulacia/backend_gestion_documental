from django.urls import path
from .views import documentos_view

urlpatterns = [
    path('', documentos_view, name='documentos_view'),
]
