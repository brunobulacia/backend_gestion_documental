from rest_framework import serializers
from .models import FlujoTrabajo, ElementoFlujo, TransicionFlujo

class FlujoTrabajoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlujoTrabajo
        fields = '__all__'

class ElementoFlujoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementoFlujo
        fields = '__all__'

class TransicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransicionFlujo
        fields = '__all__'
