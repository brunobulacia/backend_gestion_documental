from django.urls import path, re_path, include
from .views import perfil_usuario, registrar_usuario, login_usuario, get_users
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('permisos', views.PermisoViewSet)
router.register('roles', views.RolViewSet)
router.register('usuarios', views.UsuarioViewSet)
router.register('recepcionistas', views.RecepcionistaViewSet)
router.register('clientes', views.ClienteViewSet)
router.register('rol-usuarios', views.RolUsuariosViewSet)



urlpatterns = [
    path('', include(router.urls)),
    path('perfil/', perfil_usuario, name='perfil-usuario'),
    path('register/', registrar_usuario, name='registro-usuario'),
    path('login/', login_usuario, name='login'),
    path('', get_users, name='get-users'),
]
