from django.utils.dateparse import parse_date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from documentos.serializers import CrearDocumentoSerializer, DocumentoSerializer
from .models import Documento


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def documentos_view(request):
    if request.method == "GET":
        return listar_documentos(request)
    elif request.method == "POST":
        return subir_documento(request)


def subir_documento(request):
    serializer = CrearDocumentoSerializer(
        data=request.data, context={"request": request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"mensaje": "Documento subido correctamente"},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def listar_documentos(request):
    documentos = Documento.objects.all()

    tipo = request.query_params.get("tipo")
    area = request.query_params.get("area")
    fecha = request.query_params.get("fecha")
    fecha_desde = request.query_params.get("desde")
    fecha_hasta = request.query_params.get("hasta")

    if tipo:
        documentos = documentos.filter(tipo_id=tipo)
    if area:
        documentos = documentos.filter(area_id=area)
    if fecha:
        documentos = documentos.filter(fecha_creacion__date=parse_date(fecha))
    if fecha_desde and fecha_hasta:
        documentos = documentos.filter(
            fecha_creacion__date__range=(
                parse_date(fecha_desde),
                parse_date(fecha_hasta),
            )
        )

    serializer = DocumentoSerializer(documentos, many=True)
    return Response(serializer.data)
