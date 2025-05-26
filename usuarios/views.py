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
@permission_classes([AllowAny])
def login_usuario(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
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
                "rol": usuario.rol.nombre if usuario.rol else None,
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

