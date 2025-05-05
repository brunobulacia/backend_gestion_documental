from rest_framework import serializers
from .models import Usuario, Rol, Recepcionista, Cliente, Permiso, RolUsuarios
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


class RecepcionistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recepcionista
        fields = ["id", "usuario"]


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "username", "email", "rol"]


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ["username", "email", "password", "password2", "rol"]
        extra_kwargs = {
            "rol": {"required": False, "allow_null": True},
        }

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError(
                {"password": "Las contraseñas no coinciden."}
            )
        return data

    def create(self, validated_data):
        rol = validated_data.pop("rol", None)
        if rol is None:
            from usuarios.models import Rol 
            rol = Rol.objects.get(nombre__iexact="colaborador")

        validated_data.pop("password2")
        user = Usuario.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            rol=rol,
        )
        return user


class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        data.update(
            {
                "user_id": self.user.id,
                "username": self.user.username,
                "email": self.user.email,
                "rol": self.user.rol.nombre if self.user.rol else None,
            }
        )

        return data
