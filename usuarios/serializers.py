from rest_framework import serializers
from .models import (
    Rol, Permiso, RolPermisos, Funcionalidad, RolFuncionalidades,
    Planes, Organizacion, Usuario, RolUsuarios, BitacoraUsuario
)

from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ["id", "nombre"]


class RolUsuariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolUsuarios
        fields = ["id", "rol", "usuario"]



class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = ["id", "nombre"]



class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ["username", "email", "password", "password2"]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        user = Usuario.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user 


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        organizacion = self.user.organizacion
        plan = organizacion.plan if organizacion else None

        data.update({
            "user_id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "roles": [
                {
                    "id": ru.rol.id,
                    "nombre": ru.rol.nombre
                } for ru in self.user.rolusuarios_set.select_related("rol").all()
            ],
            "es_admin": self.user.es_admin,
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
            } if organizacion else None
        })

        return data


class RolPermisosSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolPermisos
        fields = ["id", "rol", "permiso"]


class FuncionalidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funcionalidad
        fields = ["id", "nombre", "descripcion"]


class RolFuncionalidadesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolFuncionalidades
        fields = ["id", "rol", "funcionalidad", "has_access"]


class PlanesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planes
        fields = [
            "id", "nombre", "descripcion", "precio", "maximo_usuarios",
            "maximo_documentos", "maximo_almacenamiento", "ocr",
            "maximo_roles", "duracion_meses"
        ]


class OrganizacionSerializer(serializers.ModelSerializer):
    plan = PlanesSerializer(read_only=True)

    class Meta:
        model = Organizacion
        fields = ["id", "nombre", "direccion", "telefono", "plan"]


class UsuarioSerializer(serializers.ModelSerializer):
    roles = RolSerializer(many=True, read_only=True)
    organizacion = OrganizacionSerializer(read_only=True)

    class Meta:
        model = Usuario
        fields = ["id", "username", "email", "roles", "organizacion", "es_admin"]
        ref_name = 'UsuarioSerializerUsuarios'

class BitacoraUsuarioSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()

    class Meta:
        model = BitacoraUsuario
        fields = '__all__'


class UsuarioWriteSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all(), many=True)

    class Meta:
        model = Usuario
        fields = ["username", "email", "roles", "es_admin"]

    def update(self, instance, validated_data):
        roles = validated_data.pop("roles", [])

        # Actualizar campos del usuario
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if roles is not None:
            # Limpiar y actualizar roles
            RolUsuarios.objects.filter(usuario=instance).delete()
            for rol in roles:
                RolUsuarios.objects.create(usuario=instance, rol=rol)

        return instance
