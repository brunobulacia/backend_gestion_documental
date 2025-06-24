from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ReglaAutomatica, EjecucionRegla
from .serializers import ReglaAutomaticaSerializer
from documentos.models import Documento
from .serializers import EjecucionReglaSerializer
from django.http import HttpResponse
from rest_framework.decorators import api_view
import io
import pandas as pd


class ReglaAutomaticaViewSet(viewsets.ModelViewSet):
    queryset = ReglaAutomatica.objects.all()
    serializer_class = ReglaAutomaticaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creada_por=self.request.user)

    @action(detail=True, methods=['patch'], url_path='activar')
    def activar(self, request, pk=None):
        regla = self.get_object()
        regla.activa = not regla.activa
        regla.save()
        estado = 'activada' if regla.activa else 'desactivada'
        return Response({'mensaje': f'Regla {estado} correctamente.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='ejecutar')
    def ejecutar_manual(self, request):
        regla_id = request.data.get('regla_id')
        contexto = request.data.get('contexto', {})
        regla = get_object_or_404(ReglaAutomatica, id=regla_id)

        resultado = 'exito'
        mensaje = 'Regla ejecutada correctamente'

        # Validar condiciones
        for clave, valor in regla.condicion.items():
            if contexto.get(clave) != valor:
                resultado = 'error'
                mensaje = f"Condición no cumplida: se esperaba '{clave} = {valor}', se recibió '{contexto.get(clave)}'"
                break

        # Ejecutar acción si condición se cumple
        if resultado == 'exito':
            try:
                if regla.accion == 'cambiar_estado':
                    documento_id = contexto.get('documento_id')
                    nuevo_estado = regla.parametros_accion.get('nuevo_estado')
                    if documento_id and nuevo_estado:
                        documento = Documento.objects.get(id=documento_id)
                        documento.estado = nuevo_estado
                        documento.save()
                        mensaje = f"Estado del documento #{documento_id} actualizado a '{nuevo_estado}'"
                    else:
                        resultado = 'error'
                        mensaje = 'Faltan parámetros para cambiar estado del documento.'
                # Aquí puedes extender con más acciones como notificar, etc.

            except Exception as e:
                resultado = 'error'
                mensaje = f"Error al ejecutar la acción: {str(e)}"

        # Registrar la ejecución
        EjecucionRegla.objects.create(
            regla=regla,
            evento=regla.evento,
            usuario=request.user,
            estado=resultado,
            mensaje=mensaje
        )

        return Response({'mensaje': mensaje, 'estado': resultado}, status=status.HTTP_200_OK)


class EjecucionReglaViewSet(viewsets.ModelViewSet):
    queryset = EjecucionRegla.objects.all().order_by('-fecha')
    serializer_class = EjecucionReglaSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
def historial_reglas_view(request):
    estado = request.GET.get('estado')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    queryset = EjecucionRegla.objects.all()

    if estado:
        queryset = queryset.filter(estado=estado)
    if fecha_inicio and fecha_fin:
        queryset = queryset.filter(fecha__range=[fecha_inicio, fecha_fin])

    serializer = EjecucionReglaSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def exportar_historial_excel(request):
    queryset = EjecucionRegla.objects.all().select_related('regla', 'usuario')
    data = [{
        "ID": e.id,
        "Regla": str(e.regla),
        "Evento": e.evento,
        "Usuario": str(e.usuario),
        "Fecha": e.fecha,
        "Estado": e.estado,
        "Mensaje": e.mensaje,
    } for e in queryset]

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Historial')
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="historial_reglas.xlsx"'
    return response


@api_view(['GET'])
def exportar_historial_pdf(request):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "Historial de Reglas Ejecutadas")

    y = 720
    for ejec in EjecucionRegla.objects.all().order_by('-fecha')[:30]:
        texto = f"{ejec.fecha.strftime('%Y-%m-%d %H:%M:%S')} | {ejec.estado.upper()} | {ejec.regla.nombre} | {ejec.usuario}"
        p.drawString(50, y, texto)
        y -= 20
        if y < 50:
            p.showPage()
            y = 750

    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
