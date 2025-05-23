# Generated by Django 5.2 on 2025-05-04 16:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentos', '0003_permisodocumento_puede_comentar_alter_documento_id_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentoversion',
            name='comentarios',
        ),
        migrations.CreateModel(
            name='ComentarioDocumento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comentario', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('autor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comentarios', to='documentos.documentoversion')),
            ],
        ),
    ]
