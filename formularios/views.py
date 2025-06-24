from rest_framework import viewsets, permissions
from .models import Formulario, CampoFormulario, RespuestaFormulario
from .serializers import FormularioSerializer, CampoFormularioSerializer, RespuestaFormularioSerializer
from rest_framework.response import Response

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

    # Filtrar campos por formulario usando el parámetro id_form en la query
    def get_queryset(self):
        queryset = super().get_queryset()
        id_form = self.request.query_params.get('id_form')
        if id_form is not None:
            try:
                id_form_int = int(str(id_form).strip().replace('/', ''))
                queryset = queryset.filter(formulario_id=id_form_int)
            except ValueError:
                queryset = queryset.none()
        return queryset

    # Listar campos de un formulario específico
    def list_by_formulario(self, request, id_form):
        queryset = self.get_queryset().filter(formulario=id_form)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class RespuestaFormularioViewSet(viewsets.ModelViewSet):
    queryset = RespuestaFormulario.objects.all()
    serializer_class = RespuestaFormularioSerializer
    permission_classes = [permissions.IsAuthenticated]
