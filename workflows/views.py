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
    TransicionSerializer,
)
from .utils import validar_estructura_flujo
from django.db import transaction
from django.db.models import Q

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def flujo_trabajo_list_create(request):
    if request.method == "GET":
        flujos = FlujoTrabajo.objects.all()
        serializer = FlujoTrabajoSerializer(flujos, many=True)
        return Response(serializer.data)

    serializer = FlujoTrabajoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(creado_por=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def flujo_trabajo_detail(request, pk):
    flujo = get_object_or_404(FlujoTrabajo, pk=pk)

    if request.method == "GET":
        serializer = FlujoTrabajoSerializer(flujo)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = FlujoTrabajoSerializer(flujo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        flujo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def crear_elemento_flujo(request):
    serializer = ElementoFlujoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def actualizar_eliminar_elemento(request, pk):
    elemento = get_object_or_404(ElementoFlujo, pk=pk)

    if request.method == "PUT":
        serializer = ElementoFlujoSerializer(elemento, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        elemento.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def crear_transicion(request):
    serializer = TransicionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def actualizar_eliminar_transicion(request, pk):
    transicion = get_object_or_404(TransicionFlujo, pk=pk)

    if request.method == "PUT":
        serializer = TransicionSerializer(transicion, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        transicion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def validar_flujo(request, flujo_id):
    flujo = get_object_or_404(FlujoTrabajo, pk=flujo_id)
    es_valido, errores = validar_estructura_flujo(flujo)
    return Response({"valido": es_valido, "errores": errores})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def asociar_flujo_tipo_documento(request, flujo_id):
    flujo = get_object_or_404(FlujoTrabajo, pk=flujo_id)
    tipo_id = request.data.get("tipo_id")
    tipo = get_object_or_404(TipoDocumento, pk=tipo_id)
    tipo.flujo = flujo
    tipo.save()
    return Response({"mensaje": "Flujo asociado correctamente al tipo de documento."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def obtener_flujo_json(request, flujo_id):
    flujo = get_object_or_404(FlujoTrabajo, pk=flujo_id)
    elementos = flujo.elementos.all()

    # Obtener transiciones donde el origen pertenece a este flujo
    transiciones = TransicionFlujo.objects.filter(origen__flujo=flujo)

    data = {
        "elementos": ElementoFlujoSerializer(elementos, many=True).data,
        "transiciones": TransicionSerializer(transiciones, many=True).data,
    }
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def actualizar_flujo(request):
    flujo_data = request.data["flujo"]
    elementos_data = request.data["elementos"]
    transiciones_data = request.data["transiciones"]

    # Actualizar flujo
    flujo = FlujoTrabajo.objects.filter(id=flujo_data["id"]).first()
    if not flujo:
        return Response(
            {"error": "Flujo no encontrado"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = FlujoTrabajoSerializer(flujo, data=flujo_data)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Guardar bpmnIds actuales para conservarlos
    bpmn_ids_elementos_actuales = []
    for elemento_data in elementos_data:
        if "bpmnId" not in elemento_data:
            return Response(
                {"error": "Falta bpmnId en un elemento"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        elemento_data["flujo"] = flujo
        bpmn_ids_elementos_actuales.append(elemento_data["bpmnId"])

        ElementoFlujo.objects.update_or_create(
            bpmnId=elemento_data["bpmnId"], defaults=elemento_data
        )

    # Eliminar elementos que ya no están en el JSON
    ElementoFlujo.objects.filter(flujo=flujo).exclude(
        bpmnId__in=bpmn_ids_elementos_actuales
    ).delete()

    # Guardar bpmnIds actuales de transiciones
    bpmn_ids_transiciones_actuales = []
    for transicion_data in transiciones_data:
        if "bpmnId" not in transicion_data:
            return Response(
                {"error": "Falta bpmnId en una transición"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        origen_id = transicion_data.pop("origen")
        destino_id = transicion_data.pop("destino")

        try:
            origen = ElementoFlujo.objects.get(id=origen_id)
            destino = ElementoFlujo.objects.get(id=destino_id)
        except ElementoFlujo.DoesNotExist:
            return Response(
                {"error": "Origen o destino no encontrado para una transición"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        transicion_data["origen"] = origen
        transicion_data["destino"] = destino
        transicion_data["flujo"] = flujo

        bpmn_ids_transiciones_actuales.append(transicion_data["bpmnId"])

        TransicionFlujo.objects.update_or_create(
            bpmnId=transicion_data["bpmnId"], defaults=transicion_data
        )

    # Eliminar transiciones que ya no están en el JSON
    TransicionFlujo.objects.filter(
        Q(origen__flujo=flujo) | Q(destino__flujo=flujo)
    ).exclude(bpmnId__in=bpmn_ids_transiciones_actuales).delete()

    return Response({"mensaje": "Flujo actualizado correctamente"})
