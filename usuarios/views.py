from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets

<<<<<<< HEAD
from usuarios.models import Usuario, Rol, Permiso, Recepcionista, RolPermisos, RolUsuarios, Cliente, BitacoraUsuario
from .serializers import RegistroUsuarioSerializer, LoginSerializer, UsuarioSerializer, PermisoSerializer, ClienteSerializer, RecepcionistaSerializer, RolSerializer, RolUsuariosSerializer, BitacoraUsuarioSerializer
=======
from usuarios.models import Usuario, Rol, Permiso, RolUsuarios, Organizacion, Planes
from .serializers import RegistroUsuarioSerializer, LoginSerializer, UsuarioSerializer, PermisoSerializer, RolSerializer, RolUsuariosSerializer, PlanesSerializer
>>>>>>> main
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class PermisoViewSet(viewsets.ModelViewSet):
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class RolUsuariosViewSet(viewsets.ModelViewSet):
    queryset = RolUsuarios.objects.all()
    serializer_class = RolUsuariosSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def suscribir_usuario(request):
    """
    Permite al usuario autenticado suscribirse a un plan.
    Crea una nueva organización y la asocia al usuario,
    si este aún no pertenece a una.
    """

    user = request.user

    if user.organizacion is not None:
        return Response(
            {"error": "El usuario ya pertenece a una organización."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    organizacion_data = request.data.get("organizacion")
    plan_id = request.data.get("plan_id")

    if not organizacion_data:
        return Response(
            {"error": "Datos de la organización no proporcionados"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        nueva_organizacion = Organizacion.objects.create(**organizacion_data)
    except Exception as e:
        return Response(
            {"error": f"No se pudo crear la organización: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if plan_id:
        try:
            plan = Planes.objects.get(id=plan_id)
            nueva_organizacion.plan = plan
            nueva_organizacion.save()
        except Planes.DoesNotExist:
            return Response(
                {"error": "Plan no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

    user.organizacion = nueva_organizacion
    user.es_admin = True
    user.save()

    return Response(
        {
            
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def obtener_plan_actual(request):
    """
    Devuelve el plan actual del usuario autenticado.

    Response:
    {
        "id": 1,
        "nombre": "PROFESIONAL",
        "descripcion": "...",
        "precio": "59.00",
        ...
    }
    """
    user = request.user
    if not user.organizacion:
        return Response({"error": "El usuario no está asociado a ninguna organización"}, status=status.HTTP_400_BAD_REQUEST)

    plan = user.organizacion.plan
    if not plan:
        return Response({"error": "La organización no tiene un plan asignado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = PlanesSerializer(plan)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def crear_usuario_en_empresa(request):
    """
    Permite a un administrador crear un usuario en su organización,
    respetando el límite máximo de usuarios definido por su plan.

    Expected JSON:
    {
        "username": "nuevo_usuario",
        "email": "nuevo@correo.com",
        "password": "unaContraseñaSegura123"
    }
    """
    admin = request.user

    if not admin.es_admin:
        return Response({"error": "No tienes permisos para realizar esta acción."}, status=status.HTTP_403_FORBIDDEN)

    if not admin.organizacion:
        return Response({"error": "Tu usuario no está asociado a una organización."}, status=status.HTTP_400_BAD_REQUEST)

    organizacion = admin.organizacion
    plan = organizacion.plan

    if not plan:
        return Response({"error": "La organización no tiene un plan asignado."}, status=status.HTTP_400_BAD_REQUEST)

    usuarios_en_organizacion = Usuario.objects.filter(organizacion=organizacion).count()

    if usuarios_en_organizacion >= plan.maximo_usuarios:
        return Response({"error": "Se ha alcanzado el número máximo de usuarios para tu plan."}, status=status.HTTP_403_FORBIDDEN)

    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not all([username, email, password]):
        return Response({"error": "Faltan campos obligatorios."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(password)
    except ValidationError as e:
        return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

    if Usuario.objects.filter(username=username).exists():
        return Response({"error": "Ya existe un usuario con ese username."}, status=status.HTTP_400_BAD_REQUEST)

    if Usuario.objects.filter(email=email).exists():
        return Response({"error": "Ya existe un usuario con ese email."}, status=status.HTTP_400_BAD_REQUEST)

    nuevo_usuario = Usuario.objects.create_user(
        username=username,
        email=email,
        password=password,
        organizacion=organizacion
    )

    serializer = UsuarioSerializer(nuevo_usuario)
    return Response({"message": "Usuario creado exitosamente", "usuario": serializer.data}, status=status.HTTP_201_CREATED)

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
def registrar_usuario(request):
    serializer = RegistroUsuarioSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save() 

        organizacion = user.organizacion
        plan = organizacion.plan if organizacion else None

        response_data = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "es_admin": user.es_admin,
            "organizacion": {
                "id": organizacion.id,
                "nombre": organizacion.nombre,
                "telefono": organizacion.telefono,
                "direccion": organizacion.direccion,
                "plan": {
                    "id": plan.id,
                    "nombre": plan.nombre,
                    "precio": float(plan.precio),
                    "maximo_usuarios": plan.maximo_usuarios,
                    "maximo_documentos": plan.maximo_documentos,
                    "maximo_almacenamiento": plan.maximo_almacenamiento,
                    "ocr": plan.ocr,
                    "maximo_roles": plan.maximo_roles,
                    "duracion_meses": plan.duracion_meses,
                } if plan else None,
            } if organizacion else None,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_users(request):
    users = Usuario.objects.all()
    serializer = UsuarioSerializer(users, many=True)
    return Response(serializer.data)

@api_view(["GET"])
<<<<<<< HEAD
@permission_classes([IsAuthenticated]) 
def ver_bitacora(request):
    if not request.user.is_staff:
        return Response({'detalle': 'No autorizado'}, status=403)

    logs = BitacoraUsuario.objects.all().order_by('-fecha')[:100]  # últimos 100 logs
    serializer = BitacoraUsuarioSerializer(logs, many=True)
    return Response(serializer.data)
=======
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def crear_rol(request):
    usuario = request.user
    organizacion = usuario.organizacion

    if not organizacion:
        return Response({"error": "El usuario no pertenece a una organización."}, status=400)

    if not usuario.es_admin:
        return Response({"error": "Solo administradores pueden crear roles."}, status=403)

    plan = organizacion.plan
    roles_actuales = Rol.objects.filter(organizacion=organizacion).count()

    if roles_actuales >= plan.maximo_roles:
        return Response({"error": "Se alcanzó el máximo de roles permitidos por el plan."}, status=403)

    nombre_rol = request.data.get("nombre")
    if not nombre_rol:
        return Response({"error": "Debe especificar un nombre para el rol."}, status=400)

    if Rol.objects.filter(nombre=nombre_rol, organizacion=organizacion).exists():
        return Response({"error": "Ya existe un rol con ese nombre en su organización."}, status=400)

    rol = Rol.objects.create(nombre=nombre_rol, organizacion=organizacion)
    return Response({"mensaje": "Rol creado correctamente", "rol_id": rol.id})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def asignar_usuario_a_rol(request):
    usuario_admin = request.user
    if not usuario_admin.es_admin:
        return Response({"error": "Solo administradores pueden asignar roles."}, status=403)

    usuario_id = request.data.get("usuario_id")
    rol_id = request.data.get("rol_id")

    if not usuario_id or not rol_id:
        return Response({"error": "Faltan datos requeridos (usuario_id, rol_id)."}, status=400)

    try:
        usuario_asignado = Usuario.objects.get(id=usuario_id)
        rol = Rol.objects.get(id=rol_id)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado."}, status=404)
    except Rol.DoesNotExist:
        return Response({"error": "Rol no encontrado."}, status=404)

    if usuario_asignado.organizacion != usuario_admin.organizacion:
        return Response({"error": "Solo puede asignar roles a usuarios de su organización."}, status=403)

    if rol.organizacion != usuario_admin.organizacion:
        return Response({"error": "No puede asignar roles de otra organización."}, status=403)

    RolUsuarios.objects.create(usuario=usuario_asignado, rol=rol)

    return Response({"mensaje": "Rol asignado correctamente."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_roles_organizacion(request):
    usuario = request.user

    if not usuario.organizacion:
        return Response({"error": "El usuario no pertenece a ninguna organización."}, status=400)

    roles = Rol.objects.filter(organizacion=usuario.organizacion)
    data = [{"id": r.id, "nombre": r.nombre} for r in roles]

    return Response(data)
>>>>>>> main
