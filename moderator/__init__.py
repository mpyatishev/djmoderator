# -*- coding: utf-8 -*-

from django.db.models import ModelBase, signals


from models import ModeratorEntry
from moderator import ModeratorBase


class AlredyRegistered(Exception):
    pass


class Moderator(object):
    def __init__(self):
        self._registered = {}

        self.init_signals()

    def register(self, models_list, moderator=None):
        if isinstance(models_list, ModelBase):
            models_list = [models_list]

        for model in models_list:
            if model not in self._registered:
                self._registered[model] = moderator or ModeratorBase
            else:
                raise AlredyRegistered('Model %s alredy registered with %s'
                                       % (model, self._registered[model]))

    def init_signals(self):
        signals.post_save.connect(self.on_post_save, weak=False)
        signals.post_delete.connect(self.on_post_delete, weak=False)

    def on_post_save(self, sender, instance, created, **kwargs):
        pass

    def on_post_delete(self, sender, instance, **kwargs):
        pass


moderator = Moderator()

default_app_config = 'moderator.app.ModeratorConfig'
