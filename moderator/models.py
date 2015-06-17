# -*- coding: utf-8 -*-


from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
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

    changes = JSONField()
