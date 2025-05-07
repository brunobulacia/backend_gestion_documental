from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import FlujoTrabajo, ElementoFlujo, TransicionFlujo
from documentos.models import TipoDocumento
from .serializers import (
    FlujoTrabajoSerializer,
    ElementoFlujoSerializer,
    TransicionSerializer
)
from .utils import validar_estructura_flujo

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def flujo_trabajo_list_create(request):
    if request.method == 'GET':
        flujos = FlujoTrabajo.objects.all()
        serializer = FlujoTrabajoSerializer(flujos, many=True)
        return Response(serializer.data)

    serializer = FlujoTrabajoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(creado_por=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def flujo_trabajo_detail(request, pk):
    flujo = get_object_or_404(FlujoTrabajo, pk=pk)

    if request.method == 'GET':
        serializer = FlujoTrabajoSerializer(flujo)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = FlujoTrabajoSerializer(flujo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        flujo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_elemento_flujo(request):
    serializer = ElementoFlujoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def actualizar_eliminar_elemento(request, pk):
    elemento = get_object_or_404(ElementoFlujo, pk=pk)

    if request.method == 'PUT':
        serializer = ElementoFlujoSerializer(elemento, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        elemento.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_transicion(request):
    serializer = TransicionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def actualizar_eliminar_transicion(request, pk):
    transicion = get_object_or_404(TransicionFlujo, pk=pk)

    if request.method == 'PUT':
        serializer = TransicionSerializer(transicion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        transicion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validar_flujo(request, flujo_id):
    flujo = get_object_or_404(FlujoTrabajo, pk=flujo_id)
    es_valido, errores = validar_estructura_flujo(flujo)
    return Response({"valido": es_valido, "errores": errores})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def asociar_flujo_tipo_documento(request, flujo_id):
    flujo = get_object_or_404(FlujoTrabajo, pk=flujo_id)
    tipo_id = request.data.get("tipo_id")
    tipo = get_object_or_404(TipoDocumento, pk=tipo_id)
    tipo.flujo = flujo
    tipo.save()
    return Response({"mensaje": "Flujo asociado correctamente al tipo de documento."})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_flujo_json(request, flujo_id):
    flujo = get_object_or_404(FlujoTrabajo, pk=flujo_id)
    elementos = flujo.elementos.all()

    # Obtener transiciones donde el origen pertenece a este flujo
    transiciones = TransicionFlujo.objects.filter(origen__flujo=flujo)

    data = {
        "elementos": ElementoFlujoSerializer(elementos, many=True).data,
        "transiciones": TransicionSerializer(transiciones, many=True).data
    }
    return Response(data)
