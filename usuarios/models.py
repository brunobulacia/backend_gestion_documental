from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


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
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)

class RolUsuarios(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

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