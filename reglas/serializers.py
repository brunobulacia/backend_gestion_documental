from rest_framework import serializers
from .models import ReglaAutomatica, EjecucionRegla


class ReglaAutomaticaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReglaAutomatica
        fields = '__all__'
        read_only_fields = ['creada_por', 'creada_en']


class EjecucionReglaSerializer(serializers.ModelSerializer):
    regla = serializers.StringRelatedField()
    usuario = serializers.StringRelatedField()

    class Meta:
        model = EjecucionRegla
        fields = ['id', 'regla', 'evento', 'usuario', 'fecha', 'estado', 'mensaje']
