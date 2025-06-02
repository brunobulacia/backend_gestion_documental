import re
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

from usuarios.models import Usuario, Rol, Permiso, Recepcionista, RolPermisos, RolUsuarios, Cliente
from .serializers import RegistroUsuarioSerializer, LoginSerializer, UsuarioSerializer, PermisoSerializer, ClienteSerializer, RecepcionistaSerializer, RolSerializer, RolUsuariosSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class PermisoViewSet(viewsets.ModelViewSet):
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class RecepcionistaViewSet(viewsets.ModelViewSet):
    queryset = Recepcionista.objects.all()
    serializer_class = RecepcionistaSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class RolUsuariosViewSet(viewsets.ModelViewSet):
    queryset = RolUsuarios.objects.all()
    serializer_class = RolUsuariosSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def perfil_usuario(request):

    """
    Devuelve el perfil del usuario autenticado.

    Returns:
    {
        "id": int,
        "username": str,
        "email": str,
        "rol": str (optional)
    }
    """
    user = request.user
    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "rol": user.rol.nombre if user.rol else None,
        }
    )


@api_view(["POST"])
def login_usuario(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        print(request.data)
        usuario = serializer.validated_data['username']
        print(usuario)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    method='post',  # lowercase 'post' instead of 'POST'
    request_body=RegistroUsuarioSerializer,
    responses={
        201: openapi.Response('User registered successfully', RegistroUsuarioSerializer),
        400: 'Bad Request'
    },
    operation_description="Registra un nuevo usuario",
    tags=["usuarios"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def registrar_usuario(request):
    serializer = RegistroUsuarioSerializer(data=request.data)
    if serializer.is_valid():
        usuario = serializer.save()

        # Generar tokens
        refresh = RefreshToken.for_user(usuario)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response(
            {
                "id": usuario.id,
                "username": usuario.username,
                "email": usuario.email,
                "access": access_token,
                "refresh": refresh_token,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_users(request):
    users = Usuario.objects.all()
    serializer = UsuarioSerializer(users, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_roles(request):
    roles = Rol.objects.all()
    serializer = RolSerializer(roles, many=True)
    return Response(serializer.data)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request):
    usuario = request.user
    try:
        user = Usuario.objects.get(id=usuario.id)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    # Extrae los roles del request
    roles_data = request.data.pop("roles", None)

    # Actualiza el usuario con el resto de los campos
    serializer = UsuarioSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

        if roles_data is not None:
            # Elimina los roles actuales
            RolUsuarios.objects.filter(usuario=user).delete()

            # Asigna los nuevos roles
            for rol_id in roles_data:
                try:
                    rol = Rol.objects.get(id=rol_id)
                    RolUsuarios.objects.create(usuario=user, rol=rol)
                except Rol.DoesNotExist:
                    continue  # Ignora IDs inválidos (puedes cambiarlo si prefieres lanzar error)

        return Response(UsuarioSerializer(user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)