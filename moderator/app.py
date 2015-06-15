# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ModeratorConfig(AppConfig):
    name = 'moderator'
    verbose_name = _("Moderation")

    def ready(self):
        print('moderator ready')
