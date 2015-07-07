# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Changes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('diff', jsonfield.fields.JSONField()),
            ],
            options={
                'ordering': ['-pk'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ModeratorEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True, editable=False, blank=True)),
                ('moderation_status', models.IntegerField(default=2, choices=[('rejected', 0), ('approved', 1), ('pending', 2)])),
                ('updated', models.DateTimeField(auto_now=True)),
                ('reason', models.TextField()),
                ('original_values', jsonfield.fields.JSONField()),
                ('content_type', models.ForeignKey(blank=True, editable=False, to='contenttypes.ContentType', null=True)),
                ('moderator', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='changes',
            name='moderator_entry',
            field=models.ForeignKey(related_name='changes', to='moderator.ModeratorEntry'),
            preserve_default=True,
        ),
    ]
