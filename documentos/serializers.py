from rest_framework import serializers
from .models import Documento, DocumentoVersion


class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = "__all__"


class DocumentoVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoVersion
        fields = ["archivo", "comentarios"]


class CrearDocumentoSerializer(serializers.ModelSerializer):
    archivo = serializers.FileField(write_only=True)
    comentarios = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

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
        comentarios = validated_data.pop("comentarios", "")

        user = self.context["request"].user
        documento = Documento.objects.create(creado_por=user, **validated_data)

        DocumentoVersion.objects.create(
            documento=documento,
            archivo=archivo,
            version=1,
            subido_por=user,
            comentarios=comentarios,
        )
        return documento
