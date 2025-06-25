from rest_framework import serializers
from .models import ReglaAutomatica, EjecucionRegla
from django.contrib.auth import get_user_model


class ReglaAutomaticaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReglaAutomatica
        fields = '__all__'
        read_only_fields = ['creada_por', 'creada_en']
 

class EjecucionReglaSerializer(serializers.ModelSerializer):
    regla = serializers.PrimaryKeyRelatedField(queryset=ReglaAutomatica.objects.all())
    usuario = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), required=False)

    class Meta:
        model = EjecucionRegla
        fields = ['id', 'regla', 'evento', 'usuario', 'fecha', 'estado', 'mensaje']
        read_only_fields = ['fecha']

    def create(self, validated_data):
        # Si usuario no viene en el request, usa el usuario autenticado
        if 'usuario' not in validated_data and self.context.get('request'):
            validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)