
from rest_framework import serializers
from .models import Formulario, CampoFormulario, RespuestaFormulario

class CampoFormularioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampoFormulario
        fields = '__all__'

class FormularioSerializer(serializers.ModelSerializer):
    campos = CampoFormularioSerializer(many=True, read_only=True)

    class Meta:
        model = Formulario
        fields = '__all__'

class RespuestaFormularioSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaFormulario
        fields = '__all__'
