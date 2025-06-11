<<<<<<< HEAD
from django.urls import path, re_path, include
from .views import perfil_usuario, registrar_usuario, login_usuario, get_users, ver_bitacora
=======
from django.urls import path, include
from .views import perfil_usuario, registrar_usuario, login_usuario, get_users, update_user, suscribir_usuario, obtener_plan_actual, crear_usuario_en_empresa, crear_rol, asignar_usuario_a_rol, listar_roles_organizacion
>>>>>>> main
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('permisos', views.PermisoViewSet)
router.register('roles', views.RolViewSet)
router.register('usuarios', views.UsuarioViewSet)
router.register('rol-usuarios', views.RolUsuariosViewSet)



urlpatterns = [
    path('', include(router.urls)),
    path('perfil/', perfil_usuario, name='perfil-usuario'),
    path('register/', registrar_usuario, name='registro-usuario'),
    path('login/', login_usuario, name='login'),
<<<<<<< HEAD
    path('', get_users, name='get-users'),
    path('bitacora/', ver_bitacora),

=======
    path('todos/', get_users, name='get-users'),
    path('update/', update_user, name='update-user'),
    path('suscribir/', suscribir_usuario, name='suscribir-usuario'),
    path('plan/', obtener_plan_actual , name='obtener-plan-actual'),
    path('agregar-usuario/', crear_usuario_en_empresa, name='agregar-usuario'),
    path('rol/', crear_rol, name='crear-rol'),
    path('asignar-rol/', asignar_usuario_a_rol, name='asignar-usuario-a-rol'),
    path('listar-roles/', listar_roles_organizacion, name='listar-roles-organizacion'),
>>>>>>> main
]
