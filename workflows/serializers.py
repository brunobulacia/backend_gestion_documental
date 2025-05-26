from rest_framework import serializers
from .models import FlujoTrabajo, ElementoFlujo, TransicionFlujo
from documentos.serializers import TipoDocumentoSerializer
from usuarios.serializers import UsuarioSerializer
from documentos.models import TipoDocumento

class FlujoTrabajoSerializer(serializers.ModelSerializer):
    tipo_documento = TipoDocumentoSerializer(read_only=True)
    creado_por = UsuarioSerializer(read_only=True)
    tipo_documento_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoDocumento.objects.all(),
        source='tipo_documento',
        write_only=True
    )

    class Meta:
        model = FlujoTrabajo
        fields = ['id', 'nombre', 'descripcion', 'tipo_documento', 'tipo_documento_id', 
                 'creado_por', 'fecha_creacion', 'activo']

class ElementoFlujoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementoFlujo
        fields = '__all__'

class TransicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransicionFlujo
        fields = '__all__'
