# -*- coding: utf-8 -*-

from dictdiffer import diff

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.core import serializers
from django.db import models
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField


MODERATION_STATUS_REJECTED = 0
MODERATION_STATUS_APPROVED = 1
MODERATION_STATUS_PENDING = 2

MODERATION_STATUS_CHOICES = (
    (_('rejected'), MODERATION_STATUS_REJECTED),
    (_('approved'), MODERATION_STATUS_APPROVED),
    (_('pending'), MODERATION_STATUS_PENDING),
)


class ModeratorEntry(models.Model):
    content_type = models.ForeignKey(ContentType, null=True, blank=True, editable=False)
    object_id = models.PositiveIntegerField(null=True, blank=True, editable=False)
    content_object = GenericForeignKey()
    moderation_status = models.IntegerField(choices=MODERATION_STATUS_CHOICES,
                                            default=MODERATION_STATUS_PENDING)
    updated = models.DateTimeField(auto_now=True)

    original_values = JSONField()

    def _serialize(self, obj=None):
        if obj is None:
            model = self.content_type.model_class()
            obj = model.objects.unmoderated().get(pk=self.object_id)
        return serializers.serialize('python', [obj])[0]

    def diff(self, other=None):
        new_values = self._serialize(other)

        if new_values != self.original_values:
            changes = self.changes.create()
            changes.diff = diff(self.original_values, new_values)
            changes.save()

            self.original_values = new_values

    def save(self, *args, **kwargs):
        if not self.pk:
            self.original_values = self._serialize(self.content_object)
        super(ModeratorEntry, self).save(*args, **kwargs)


class Changes(models.Model):
    moderator_entry = models.ForeignKey(ModeratorEntry, related_name='changes')
    created = models.DateTimeField(auto_now_add=True)
    diff = JSONField()

    class Meta:
        ordering = ['-pk']
