# -*- coding: utf-8 -*-

from django.db.models import signals
from django.db.models.base import ModelBase


from managers import ModeratorManagerFactory
from models import ModeratorEntry


class AlredyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class ModeratorBase(object):
    managers = ['objects']


class Moderator(object):
    def __init__(self):
        self._registered = {}

    def register(self, models_list, moderator=None):
        if isinstance(models_list, ModelBase):
            models_list = [models_list]

        moderator = moderator or ModeratorBase

        for model in models_list:
            if model not in self._registered:
                self._registered[model] = moderator
                self.init_signals(model)
                self.update_managers(model, moderator)
            else:
                raise AlredyRegistered('Model %s alredy registered with %s'
                                       % (model, self._registered[model]))

    def unregister(self, models_list):
        if isinstance(models_list, ModelBase):
            models_list = [models_list]

        for model in models_list:
            if model in self._registered:
                del self._registered[model]
            else:
                raise NotRegistered('Model %s not registered' % model)

    def init_signals(self, model):
        signals.post_save.connect(self.on_post_save, sender=model, weak=False)

    def on_post_save(self, sender, instance, created, **kwargs):
        pass

    def update_managers(self, model, moderator):
        for manager_name in moderator.managers:
            if hasattr(model, manager_name):
                manager = getattr(model, manager_name).__class__
                new_manager = ModeratorManagerFactory.get(bases=manager)
                model.add_to_class(manager_name, new_manager())


moderator = Moderator()

default_app_config = 'moderator.app.ModeratorConfig'
