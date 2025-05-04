from django.urls import path
from .views import perfil_usuario, registrar_usuario, login_usuario

urlpatterns = [
    path('perfil/', perfil_usuario, name='perfil-usuario'),
    path('register/', registrar_usuario, name='registro-usuario'),
    path('login/', login_usuario, name='login'),
]
