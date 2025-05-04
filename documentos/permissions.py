from .models import PermisoDocumento, Documento

def puede_editar(usuario, documento):
    '''
    Devuelve True si el usuario puede editar el documento
    '''
    if not usuario.is_authenticated:
        return False
    try:
        permiso = PermisoDocumento.objects.get(usuario=usuario, documento=documento)
        return permiso.puede_editar
    except PermisoDocumento.DoesNotExist:
        return False

def puede_ver(usuario, documento):
    '''
    Devuelve True si el usuario puede ver el documento
    '''
    if not usuario.is_authenticated:
        return False
    try:
        permiso = PermisoDocumento.objects.get(usuario=usuario, documento=documento)
        return permiso.puede_ver
    except PermisoDocumento.DoesNotExist:
        return False

def puede_comentar(usuario, documento):
    '''
    Devuelve True si el usuario puede comentar el documento
    '''
    if not usuario.is_authenticated:
        return False
    try:
        permiso = PermisoDocumento.objects.get(usuario=usuario, documento=documento)
        return permiso.puede_comentar
    except PermisoDocumento.DoesNotExist:
        return False

def puede_editar_permisos(usuario, documento):
    '''
    Devuelve True si el usuario puede editar los permisos del documento
    '''
    if not usuario.is_authenticated:
        return False
    try:
        documento = Documento.objects.get(documento=documento)
        return documento.creado_por == usuario or usuario.is_superuser
    except PermisoDocumento.DoesNotExist:
        return False
    
