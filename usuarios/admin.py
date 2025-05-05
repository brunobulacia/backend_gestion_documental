from django.contrib import admin
from .models import Rol
from .models import Permiso, RolUsuarios, Usuario

admin.site.register(Permiso)
admin.site.register(RolUsuarios)
admin.site.register(Usuario)



@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)