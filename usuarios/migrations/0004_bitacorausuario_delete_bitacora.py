# Generated by Django 5.2.2 on 2025-06-11 16:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0003_rol_organizacion'),
    ]

    operations = [
        migrations.CreateModel(
            name='BitacoraUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
                ('accion', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('endpoint', models.CharField(max_length=255)),
                ('metodo', models.CharField(max_length=10)),
                ('user_agent', models.TextField(blank=True)),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Bitacora',
        ),
    ]
