from rest_framework import serializers
from .models import (
    ComentarioDocumento,
    Documento,
    DocumentoVersion,
    TipoDocumento,
    Area,
    MetadatoPersonalizado,
    PermisoDocumento,
)
from usuarios.models import Organizacion, Usuario
from rest_framework.request import Request


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "username", "email"]
        ref_name = "UsuarioSerializerDocumento"


class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ["id", "nombre"]


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "nombre"]


class DocumentoVersionSerializer(serializers.ModelSerializer):
    subido_por = UsuarioSerializer()
    documento_id = serializers.UUIDField(source="documento.id")

    class Meta:
        model = DocumentoVersion
        fields = [
            "id",
            "documento_id",
            "archivo",
            "version",
            "subido_por",
            "fecha_subida",
            "comentarios",
        ]


class MetadatoPersonalizadoSerializer(serializers.ModelSerializer):
    documento_id = serializers.UUIDField(source="documento.id")

    class Meta:
        model = MetadatoPersonalizado
        fields = ["id", "documento_id", "clave", "valor"]


class PermisoDocumentoSerializer(serializers.ModelSerializer):
    documento_id = serializers.UUIDField(source="documento.id")
    usuario = UsuarioSerializer()

    class Meta:
        model = PermisoDocumento
        fields = [
            "id",
            "documento_id",
            "usuario",
            "puede_ver",
            "puede_editar",
        ]


class CrearDocumentoSerializer(serializers.ModelSerializer):
    archivo = serializers.FileField(write_only=True)
    comentarios = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    tipo = serializers.PrimaryKeyRelatedField(queryset=TipoDocumento.objects.all())
    area = serializers.PrimaryKeyRelatedField(queryset=Area.objects.all())

    class Meta:
        model = Documento
        fields = [
            "titulo",
            "descripcion",
            "tipo",
            "area",
            "es_publico",
            "archivo",
            "comentarios",
        ]

    def create(self, validated_data):
        archivo = validated_data.pop("archivo")
        comentario_texto = validated_data.pop("comentarios", "").strip()

        user = self.context["request"].user
        organizacion = user.organizacion  # se asume validado en la view

        documento = Documento.objects.create(
            creado_por=user, organizacion=organizacion, **validated_data
        )

        version = DocumentoVersion.objects.create(
            documento=documento,
            archivo=archivo,
            version=1,
            subido_por=user,
        )

        if comentario_texto:
            ComentarioDocumento.objects.create(
                version=version, autor=user, comentario=comentario_texto
            )

        return documento


class DocumentoSerializer(serializers.ModelSerializer):
    tipo = TipoDocumentoSerializer()
    area = AreaSerializer()
    versiones = DocumentoVersionSerializer(many=True, read_only=True)
    metadatos = MetadatoPersonalizadoSerializer(many=True, read_only=True)
    permisos = PermisoDocumentoSerializer(many=True, read_only=True)
    creado_por = UsuarioSerializer()

    class Meta:
        model = Documento
        fields = [
            "id",
            "titulo",
            "descripcion",
            "tipo",
            "area",
            "es_publico",
            "versiones",
            "metadatos",
            "permisos",
            "fecha_creacion",
            "fecha_modificacion",
            "creado_por",
        ]


class ComentarioDocumentoSerializer(serializers.ModelSerializer):
    autor_username = serializers.CharField(source="autor.username", read_only=True)

    class Meta:
        model = ComentarioDocumento
        fields = [
            "id",
            "version",
            "autor",
            "autor_username",
            "comentario",
            "fecha",
            "es_publico",
            "rol",
        ]
        read_only_fields = ["autor", "fecha", "rol"]


class ComentarioDocumentoSerializer(serializers.ModelSerializer):
    autor_username = serializers.CharField(source="autor.username", read_only=True)

    class Meta:
        model = ComentarioDocumento
        fields = [
            "id",
            "version",
            "autor",
            "autor_username",
            "comentario",
            "fecha",
            "es_publico",
            "rol",
        ]
        read_only_fields = ["autor", "fecha", "rol"]


class FiltroMetadatosSerializer(serializers.Serializer):
    tipo_documento = serializers.CharField(required=False)
    area = serializers.CharField(required=False)
    fecha_desde = serializers.DateField(required=False)
    fecha_hasta = serializers.DateField(required=False)
    metadatos = serializers.JSONField(required=False)
