from django.contrib import admin

# Register your models here.
from .models import Documento, DocumentoVersion, PermisoDocumento, TipoDocumento, Area, MetadatoPersonalizado, ComentarioDocumento

admin.site.register(Documento)
admin.site.register(DocumentoVersion)
admin.site.register(PermisoDocumento)
admin.site.register(TipoDocumento)
admin.site.register(Area)
admin.site.register(MetadatoPersonalizado)
admin.site.register(ComentarioDocumento)
