from django.utils.dateparse import parse_date
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from documentos.serializers import AreaSerializer, CrearDocumentoSerializer, DocumentoSerializer, DocumentoVersionSerializer, ComentarioDocumentoSerializer, FiltroMetadatosSerializer, TipoDocumentoSerializer
from .models import Area, Documento, DocumentoVersion, ComentarioDocumento, PermisoDocumento, TipoDocumento, MetadatoPersonalizado
from usuarios.models import BitacoraUsuario
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
import os
from django.utils.timezone import now, timedelta

#busqueda avanzada
class DocumentoViewSet(viewsets.ModelViewSet):
    queryset = Documento.objects.all()
    serializer_class = DocumentoSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'area', 'es_publico', 'fecha_creacion']
    search_fields = ['titulo', 'descripcion']

    def get_queryset(self):
        queryset = super().get_queryset()
        clave = self.request.query_params.get('metadato_clave')
        valor = self.request.query_params.get('metadato_valor')

        if clave and valor:
            queryset = queryset.filter(metadatos__clave__icontains=clave,
                                       metadatos__valor__icontains=valor).distinct()
        elif clave:
            queryset = queryset.filter(metadatos__clave__icontains=clave).distinct()
        elif valor:
            queryset = queryset.filter(metadatos__valor__icontains=valor).distinct()

        return queryset
    

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def documentos_view(request):
    if request.method == "GET":
        return listar_documentos(request)
    elif request.method == "POST":
        return subir_documento(request)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def subir_documento(request):
    usuario = request.user
    print("hola")
    if not usuario.organizacion:
        
        return Response(
            {"error": "El usuario no está asociado a ninguna organización."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    organizacion = usuario.organizacion
    plan = organizacion.plan
    
    # Verifica si el plan permite documentos ilimitados
    if plan.maximo_documentos is not None:
        documentos_actuales = Documento.objects.filter(organizacion=organizacion).count()

        if documentos_actuales >= plan.maximo_documentos:
            return Response(
                {"error": "Se ha alcanzado el límite de documentos el plan de su organizacion."},
                status=status.HTTP_403_FORBIDDEN,
            )
    
    serializer = CrearDocumentoSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        BitacoraUsuario.objects.create(
        usuario=request.user,
        ip=get_client_ip(request),
        accion="Subió un documento",
        endpoint=request.path,
        metodo=request.method,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
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
    BitacoraUsuario.objects.create(
        usuario=request.user,
        ip=get_client_ip(request),
        accion="Listó los documentos",
        endpoint=request.path,
        metodo=request.method,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
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
        # comentarios=comentarios
    )
    BitacoraUsuario.objects.create(
        usuario=request.user,
        ip=get_client_ip(request),
        accion="Creó una nueva verision del documento",
        endpoint=request.path,
        metodo=request.method,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
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
    BitacoraUsuario.objects.create(
        usuario=request.user,
        ip=get_client_ip(request),
        accion="Creó un tipo de documento",
        endpoint=request.path,
        metodo=request.method,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    return Response({'id': tipo.id, 'nombre': tipo.nombre}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_area(request):
    nombre = request.data.get('nombre')
    if not nombre:
        return Response({'detail': 'Falta el nombre'}, status=400)

    area = Area.objects.create(nombre=nombre)
    BitacoraUsuario.objects.create(
        usuario=request.user,
        ip=get_client_ip(request),
        accion="Creó un area",
        endpoint=request.path,
        metodo=request.method,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
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
    BitacoraUsuario.objects.create(
        usuario=request.user,
        ip=get_client_ip(request),
        accion="Accedió al resumen de documentos",
        endpoint=request.path,
        metodo=request.method,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    return Response({
        'documentos': documentos_serializados,
        'tipos_documento': list(tipos),
        'areas': list(areas),
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restaurar_version(request, documento_id, version_id):
    try:
        documento = Documento.objects.get(id=documento_id)
        version = DocumentoVersion.objects.get(id=version_id, documento = documento)
    except (Documento.DoesNotExist, DocumentoVersion.DoesNotExist):
        return Response({'detalle': 'El Documento o versión no se encuentra'}, status=status.HTTP_404_NOT_FOUND)
    
    nueva_version = DocumentoVersion.objects.create(
        documento=documento,
        archivo=version.archivo,
        version=documento.versiones.first().version + 1,
        subido_por=request.user
    )
    ComentarioDocumento.objects.create(
        version=nueva_version,
        autor=request.user,
        comentario=f"Restauración de la version {version.version}"
    )
    BitacoraUsuario.objects.create(
        usuario=request.user,
        ip=get_client_ip(request),
        accion="Restauró una version del documento",
        endpoint=request.path,
        metodo=request.method,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    return Response({'detalle': 'Se restauró la version exitosamente', 'nueva_version': nueva_version.version})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ver_permisos_documento(request, documento_id):
    try:
        documento = Documento.objects.get(id=documento_id)
    except Documento.DoesNotExist:
        return Response({'detalle':'Documento no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    permisos = PermisoDocumento.objects.filter(documento=documento).select_related('usuario')
    permisos_data = [
        {
            'usuario': permiso.usuario.username,
            'puede_ver': permiso.puede_ver,
            'puede_editar': permiso.puede_editar,
            'puede_comentar': permiso.puede_comentar
        }
        for permiso in permisos
    ]
    return Response(permisos_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def descargar_documento(request, version_id):
    try:
        version = DocumentoVersion.objects.get(id=version_id)
        archivo = version.archivo
        if not archivo:
            return Response({'detalle': 'Archivo no encontrado'}, status=status.HTTP_400_BAD_REQUEST)
        BitacoraUsuario.objects.create(
        usuario=request.user,
        ip=get_client_ip(request),
        accion="Descargó un documento",
        endpoint=request.path,
        metodo=request.method,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        return FileResponse(archivo.open(), as_attachment=True, filename=archivo.name.split('/')[-1])
    except DocumentoVersion.DoesNotExist:
        return Response({'detalle':'Version no encontrada'}, status=status.HTTP_400_BAD_REQUEST)

#endpoints para la gestion de comentarios
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_comentarios_version(request, version_id):
    try:
        version = DocumentoVersion.objects.get(id=version_id)
    except DocumentoVersion.DoesNotExist:
        return Response({'detalle': 'Versión no encontrada'}, status=404)

    comentarios = ComentarioDocumento.objects.filter(version=version)
    serializer = ComentarioDocumentoSerializer(comentarios, many=True)
    BitacoraUsuario.objects.create(
        usuario=request.user,
        ip=get_client_ip(request),
        accion="Listó los comentarios",
        endpoint=request.path,
        metodo=request.method,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_comentario(request, version_id):
    try:
        version = DocumentoVersion.objects.get(id=version_id)
    except DocumentoVersion.DoesNotExist:
        return Response({'detalle': 'Versión no encontrada'}, status=404)

    data = request.data.copy()
    data['version'] = version.id
    serializer = ComentarioDocumentoSerializer(data=data)

    if serializer.is_valid():
        serializer.save(autor=request.user, equipo=request.user.equipo, rol=request.user.rol)
        BitacoraUsuario.objects.create(
        usuario=request.user,
        ip=get_client_ip(request),
        accion="Creó un comentario",
        endpoint=request.path,
        metodo=request.method,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_comentario(request, comentario_id):
    try:
        comentario = ComentarioDocumento.objects.get(id=comentario_id)
    except ComentarioDocumento.DoesNotExist:
        return Response({'detalle': 'Comentario no encontrado'}, status=404)

    # Opcional: solo autor o admin pueden borrar
    if comentario.autor != request.user and not request.user.is_staff:
        return Response({'detalle': 'No autorizado'}, status=403)
    BitacoraUsuario.objects.create(
        usuario=request.user,
        ip=get_client_ip(request),
        accion="eliminó un comentario",
        endpoint=request.path,
        metodo=request.method,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    comentario.delete()
    return Response({'detalle': 'Comentario eliminado'}, status=204)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_documentos(request):
    serializer = FiltroMetadatosSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Filtros básicos (tipo, área, fecha)
    documentos = Documento.objects.all()
    if serializer.validated_data.get('tipo_documento'):
        documentos = documentos.filter(tipo__nombre=serializer.validated_data['tipo_documento'])
    if serializer.validated_data.get('area'):
        documentos = documentos.filter(area__nombre=serializer.validated_data['area'])
    if serializer.validated_data.get('fecha_desde') and serializer.validated_data.get('fecha_hasta'):
        documentos = documentos.filter(
            fecha_creacion__date__range=(
                serializer.validated_data['fecha_desde'],
                serializer.validated_data['fecha_hasta']
            )
        )

    # Filtros por metadatos (si existen)
    if serializer.validated_data.get('metadatos'):
        for clave, valor in serializer.validated_data['metadatos'].items():
            documentos = documentos.filter(
                metadatos__clave=clave,
                metadatos__valor=valor
            )

    # Optimización de consultas
    documentos = documentos.prefetch_related('metadatos', 'versiones').select_related('tipo', 'area')
    return Response(DocumentoSerializer(documentos, many=True).data)

def descargar_version(request, version_id):
    version = get_object_or_404(DocumentoVersion, id=version_id)

    if not version.archivo:
        raise Http404("El archivo no está disponible.")

    # Aquí puedes validar permisos si es necesario, por ejemplo:
    # if not request.user.has_perm("ver_documento", version.documento):
    #     raise PermissionDenied()
    BitacoraUsuario.objects.create(
        usuario=request.user,
        ip=get_client_ip(request),
        accion="Descargó la version de un documento",
        endpoint=request.path,
        metodo=request.method,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    return FileResponse(
        version.archivo.open("rb"),
        as_attachment=True,
        filename=os.path.basename(version.archivo.name)
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agregar_metadatos(request, documento_id):
    try:
        documento = Documento.objects.get(id=documento_id)
    except Documento.DoesNotExist:
        return Response({'detalle': 'Documento no encontrado'}, status=404)

    data = request.data.copy()
    
    # Obtener los IDs de los metadatos actuales del documento
    metadatos_actuales = MetadatoPersonalizado.objects.filter(documento=documento)
    ids_actuales = set(metadatos_actuales.values_list('id', flat=True))
    
    # Conjunto de IDs en la nueva solicitud
    ids_nuevos = set(metadato.get('id') for metadato in data if metadato.get('id'))
    
    # Eliminar metadatos que ya no están en la solicitud
    ids_a_eliminar = ids_actuales - ids_nuevos
    if ids_a_eliminar:
        metadatos_actuales.filter(id__in=ids_a_eliminar).delete()
    
    # Crear o actualizar metadatos
    print(data)
    for metadato in data:
        if metadato.get('id') is not None:
            # Actualizar metadato existente
            MetadatoPersonalizado.objects.filter(
                id=metadato['id'],
                documento=documento
            ).update(
                clave=metadato['clave'],
                valor=metadato['valor']
            )
        else:
            # Crear nuevo metadato
            MetadatoPersonalizado.objects.create(
                documento=documento,
                clave=metadato['clave'],
                valor=metadato['valor'],
                tipo_dato='texto'
            )
    BitacoraUsuario.objects.create(
        usuario=request.user,
        ip=get_client_ip(request),
        accion="Agregó los metadatos de un documento",
        endpoint=request.path,
        metodo=request.method,
        user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
    return Response({
        'detalle': 'Metadatos actualizados correctamente',
        'metadatos_eliminados': len(ids_a_eliminar),
        'metadatos_actualizados': len(data)
    }, status=200)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_tipos_documentos(request):
    tipos = TipoDocumento.objects.all()
    serializer = TipoDocumentoSerializer(tipos, many=True)
    return Response(serializer.data)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    usuario = request.user

    if usuario.organizacion:
        documentos = Documento.objects.filter(organizacion=usuario.organizacion).prefetch_related('versiones', 'permisos', 'tipo', 'area', 'creado_por')
        print(documentos)
    else:
        print("entro")
        documentos = Documento.objects.filter(
            Q(creado_por=usuario) | Q(permisos__usuario=usuario)
        ).distinct().prefetch_related('versiones', 'permisos', 'tipo', 'area', 'creado_por')
        print(documentos)

    tipos = TipoDocumento.objects.all()
    areas = Area.objects.all()

    total_documentos = documentos.count()
    documentos_publicos = documentos.filter(es_publico=True).count()
    documentos_privados = total_documentos - documentos_publicos
    total_versiones = DocumentoVersion.objects.filter(documento__in=documentos).count()

    # Para tendencia: cambio de cantidad de documentos en últimos 30 días vs anteriores 30 días
    hoy = now().date()
    hace_30 = hoy - timedelta(days=30)
    hace_60 = hoy - timedelta(days=60)

    docs_ultimos_30 = documentos.filter(fecha_creacion__gte=hace_30).count()
    docs_previos_30 = documentos.filter(fecha_creacion__gte=hace_60, fecha_creacion__lt=hace_30).count()
    documentos_trend = _trend_percent(docs_previos_30, docs_ultimos_30)

    vers_ultimos_30 = DocumentoVersion.objects.filter(documento__in=documentos, fecha_subida__gte=hace_30).count()
    vers_previos_30 = DocumentoVersion.objects.filter(documento__in=documentos, fecha_subida__gte=hace_60, fecha_subida__lt=hace_30).count()
    versiones_trend = _trend_percent(vers_previos_30, vers_ultimos_30)

    publicos_trend = _trend_percent(
        documentos.filter(es_publico=True, fecha_creacion__gte=hace_60, fecha_creacion__lt=hace_30).count(),
        documentos.filter(es_publico=True, fecha_creacion__gte=hace_30).count()
    )

    privados_trend = _trend_percent(
        documentos.filter(es_publico=False, fecha_creacion__gte=hace_60, fecha_creacion__lt=hace_30).count(),
        documentos.filter(es_publico=False, fecha_creacion__gte=hace_30).count()
    )

    # Documentos recientes
    documentos_recientes = documentos.order_by('-fecha_modificacion')[:5]
    hoy_dt = now()
    documentos_recientes_data = []
    for doc in documentos_recientes:
        dias = (hoy_dt - doc.fecha_modificacion).days
        doc_serialized = DocumentoSerializer(doc).data
        doc_serialized['diasDesdeModificacion'] = dias
        documentos_recientes_data.append(doc_serialized)

    # Actividad reciente (creación y versión)
    actividad = []
    for doc in documentos:
        actividad.append({
            'id': f'creacion-{doc.id}',
            'tipo': 'creacion',
            'titulo': doc.titulo,
            'usuario': {
                'id': doc.creado_por.id,
                'username': doc.creado_por.username
            },
            'fecha': doc.fecha_creacion,
            'descripcion': f'{doc.creado_por.username} creó "{doc.titulo}"',
            'color': 'var(--color-primary)'
        })
        if doc.versiones.count() > 1:
            ultima_version = doc.versiones.order_by('-version').first()
            actividad.append({
                'id': f'version-{ultima_version.id}',
                'tipo': 'version',
                'titulo': doc.titulo,
                'usuario': {
                    'id': ultima_version.subido_por.id if ultima_version.subido_por else None,
                    'username': ultima_version.subido_por.username if ultima_version.subido_por else 'Desconocido'
                },
                'fecha': ultima_version.fecha_subida,
                'descripcion': f'{ultima_version.subido_por.username if ultima_version.subido_por else "Alguien"} subió nueva versión de "{doc.titulo}"',
                'color': 'var(--color-info)'
            })

    actividad = sorted(actividad, key=lambda x: x['fecha'], reverse=True)[:8]

    # Documentos compartidos
    documentos_compartidos = documentos.exclude(creado_por=usuario).filter(permisos__usuario=usuario).distinct()[:5]

    return Response({
        'documentos': DocumentoSerializer(documentos, many=True).data,
        'tipos_documento': TipoDocumentoSerializer(tipos, many=True).data,
        'areas': AreaSerializer(areas, many=True).data,

        'total_documentos': total_documentos,
        'documentos_publicos': documentos_publicos,
        'documentos_privados': documentos_privados,
        'total_versiones': total_versiones,
        'documentos_trend': documentos_trend,
        'versiones_trend': versiones_trend,
        'publicos_trend': publicos_trend,
        'privados_trend': privados_trend,

        'documentos_recientes': documentos_recientes_data,
        'actividad_reciente': actividad,
        'documentos_compartidos': DocumentoSerializer(documentos_compartidos, many=True).data,
    })


def _trend_percent(anterior, actual):
    if anterior == 0 and actual == 0:
        return 0
    if anterior == 0:
        return 100
    return int(((actual - anterior) / anterior) * 100)