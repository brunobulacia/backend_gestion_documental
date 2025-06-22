from rest_framework import viewsets, permissions
from .models import Formulario, CampoFormulario, RespuestaFormulario
from .serializers import FormularioSerializer, CampoFormularioSerializer, RespuestaFormularioSerializer


class FormularioViewSet(viewsets.ModelViewSet):
    queryset = Formulario.objects.all()
    serializer_class = FormularioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)


class CampoFormularioViewSet(viewsets.ModelViewSet):
    queryset = CampoFormulario.objects.all()
    serializer_class = CampoFormularioSerializer
    permission_classes = [permissions.IsAuthenticated]


class RespuestaFormularioViewSet(viewsets.ModelViewSet):
    queryset = RespuestaFormulario.objects.all()
    serializer_class = RespuestaFormularioSerializer
    permission_classes = [permissions.IsAuthenticated]
