from django.contrib.auth.models import AbstractUser
from django.db import models


class Rol(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre


class Permiso(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class RolPermisos(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)


class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    roles = models.ManyToManyField(Rol, through='RolUsuarios')

class RolUsuarios(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_asignacion = models.DateTimeField(auto_now_add=True, null=True)

class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    ci = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    sexo = models.CharField(
        max_length=1, choices=[("M", "Masculino"), ("F", "Femenino")]
    )
    telefono = models.CharField(max_length=20)

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


class Funcionalidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    
class RolFuncionalidades(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    funcionalidad = models.ForeignKey(Funcionalidad, on_delete=models.CASCADE)
    has_access = models.BooleanField(default=False)