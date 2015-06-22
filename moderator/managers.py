# -*- coding: utf-8 -*-


from django.db import models

from models import MODERATION_STATUS_APPROVED


class MetaManager(type(models.Manager)):
    def __new__(cls, name, bases, attrs):
        return super(MetaManager, cls).__new__(cls, name, bases, attrs)


class ModeratorManagerFactory(object):
    @staticmethod
    def get(bases):
        if not isinstance(bases, tuple):
            bases = (bases,)

        bases = (ModeratorManager,) + bases

        return MetaManager(ModeratorManager.__name__, bases,
                           {'use_for_related_fields': True})


class ModeratorManager(models.Manager):
    def get_queryset(self):
        return super(ModeratorManager, self).get_queryset()\
            .filter(moderator_entry__moderation_status=MODERATION_STATUS_APPROVED)

    def unmoderated(self):
        return super(ModeratorManager, self).get_queryset()
