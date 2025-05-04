from django.utils.dateparse import parse_date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from documentos.serializers import CrearDocumentoSerializer, DocumentoSerializer, DocumentoVersionSerializer
from .models import Area, Documento, DocumentoVersion, PermisoDocumento, TipoDocumento
from django.db.models import Q

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def historial_versiones(request, documento_id):
    try:
        documento = Documento.objects.get(id=documento_id)
    except Documento.DoesNotExist:
        return Response({'detail': 'Documento no encontrado'}, status=404)

    versiones = documento.versiones.all()
    serializer = DocumentoVersionSerializer(versiones, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def asignar_permiso(request, documento_id):
    try:
        documento = Documento.objects.get(id=documento_id)
    except Documento.DoesNotExist:
        return Response({'detail': 'Documento no encontrado'}, status=404)

    data = request.data
    permiso, created = PermisoDocumento.objects.update_or_create(
        documento=documento,
        usuario_id=data.get("usuario_id"),
        defaults={
            "puede_ver": data.get("puede_ver", True),
            "puede_editar": data.get("puede_editar", False),
            "puede_comentar": data.get("puede_comentar", False),
        }
    )
    return Response({"detalle": "Permiso asignado correctamente"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subir_nueva_version(request, documento_id):
    try:
        documento = Documento.objects.get(id=documento_id)
    except Documento.DoesNotExist:
        return Response({'detail': 'Documento no encontrado'}, status=404)

    archivo = request.FILES.get('archivo')
    comentarios = request.data.get('comentarios', '')

    if not archivo:
        return Response({'detail': 'Se requiere un archivo'}, status=400)

    # Obtener la última versión
    ultima_version = documento.versiones.first()
    nueva_version = 1 if not ultima_version else ultima_version.version + 1

    version = DocumentoVersion.objects.create(
        documento=documento,
        archivo=archivo,
        version=nueva_version,
        subido_por=request.user,
        comentarios=comentarios
    )

    return Response({
        'detalle': 'Nueva versión subida',
        'version': version.version
    }, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_tipo_documento(request):
    nombre = request.data.get('nombre')
    if not nombre:
        return Response({'detail': 'Falta el nombre'}, status=400)

    tipo = TipoDocumento.objects.create(nombre=nombre)
    return Response({'id': tipo.id, 'nombre': tipo.nombre}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_area(request):
    nombre = request.data.get('nombre')
    if not nombre:
        return Response({'detail': 'Falta el nombre'}, status=400)

    area = Area.objects.create(nombre=nombre)
    return Response({'id': area.id, 'nombre': area.nombre}, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resumen_documentos(request):
    usuario = request.user

    documentos_con_permiso = Documento.objects.filter(
        permisos__usuario=usuario,
        permisos__puede_ver=True
    ).distinct()

    documentos = Documento.objects.filter(
        Q(id__in=documentos_con_permiso) |
        Q(es_publico=True) |
        Q(creado_por=usuario)
    ).prefetch_related(
        'versiones', 'metadatos', 'permisos', 'tipo', 'area'
    ).select_related('creado_por', 'tipo', 'area').distinct()

    documentos_serializados = DocumentoSerializer(documentos, many=True).data

    tipos = TipoDocumento.objects.values('id', 'nombre')
    areas = Area.objects.values('id', 'nombre')

    return Response({
        'documentos': documentos_serializados,
        'tipos_documento': list(tipos),
        'areas': list(areas),
    })

