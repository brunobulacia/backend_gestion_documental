from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings




class Planes(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    maximo_usuarios = models.PositiveIntegerField()
    maximo_documentos = models.PositiveIntegerField()
    maximo_almacenamiento = models.PositiveIntegerField()
    ocr = models.BooleanField(default=False)
    maximo_roles = models.PositiveIntegerField()
    duracion_meses = models.PositiveIntegerField()

    def __str__(self):
        return self.nombre


class Organizacion(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    plan = models.ForeignKey(Planes, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre

class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE, related_name='roles', null=True, blank=True)
    
    def __str__(self):
        return self.nombre


class Permiso(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class RolPermisos(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)


class Funcionalidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre


class RolFuncionalidades(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    funcionalidad = models.ForeignKey(Funcionalidad, on_delete=models.CASCADE)
    has_access = models.BooleanField(default=False)


class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    es_admin = models.BooleanField(default=False)
    roles = models.ManyToManyField(Rol, through='RolUsuarios')
    organizacion = models.ForeignKey(Organizacion, on_delete=models.SET_NULL, null=True, blank=True)


class RolUsuarios(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True, null=True)


<<<<<<< HEAD
class Recepcionista(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    ci = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    sexo = models.CharField(
        max_length=1, choices=[("M", "Masculino"), ("F", "Femenino")]
    )
    telefono = models.CharField(max_length=20)
    cargo = models.CharField(max_length=100)


class BitacoraUsuario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    ip = models.GenericIPAddressField()
    accion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    endpoint = models.CharField(max_length=255)
    metodo = models.CharField(max_length=10)
    user_agent = models.TextField(blank=True)

    def __str__(self):
        return f"[{self.fecha}] {self.usuario} - {self.accion}"
=======
class Bitacora(models.Model):
    usuario = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    accion = models.CharField(max_length=255)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    hash_transaccion = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.accion} - {self.fecha}"
>>>>>>> main
