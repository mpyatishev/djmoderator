# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericRelation
from django.db.models import signals
from django.db.models.base import ModelBase


from managers import ModeratorManagerFactory
from models import (
    ModeratorEntry,

    MODERATION_STATUS_PENDING,
)


class AlredyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class ModeratorBase(object):
    managers = ['objects']


class Moderator(object):
    def __init__(self):
        self._registered = {}

    def register(self, models_list, moderator=None, with_related=False):
        if isinstance(models_list, ModelBase):
            models_list = [models_list]

        if with_related:
            related =[]
            for model in models_list:
             related += self.get_related_models(model)
            models_list += related

        moderator = moderator or ModeratorBase

        for model in models_list:
            if model not in self._registered:
                self._registered[model] = moderator
                self.add_moderator_entry(model)
                self.update_managers(model, moderator)
                self.init_signals(model)
            else:
                raise AlredyRegistered('Model %s alredy registered with %s'
                                       % (model, self._registered[model]))

    def unregister(self, models_list):
        if isinstance(models_list, ModelBase):
            models_list = [models_list]

        for model in models_list:
            if model in self._registered:
                del self._registered[model]
                self.disconnect_signals(model)
                self.remove_moderator_entry(model)
            else:
                raise NotRegistered('Model %s not registered' % model)

    def init_signals(self, model):
        signals.post_save.connect(self.on_post_save, sender=model, weak=False)

    def disconnect_signals(self, model):
        signals.post_save.disconnect(self.on_post_save, sender=model)

    def on_post_save(self, sender, instance, **kwargs):
        me, created = ModeratorEntry.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(sender),
            object_id=instance.pk
        )

        if not created:
            me.diff()

        me.moderation_status = MODERATION_STATUS_PENDING
        me.save()

    def update_managers(self, model, moderator):
        for manager_name in moderator.managers:
            if hasattr(model, manager_name):
                manager = getattr(model, manager_name).__class__
                new_manager = ModeratorManagerFactory.get(bases=manager)
                model.add_to_class(manager_name, new_manager())

    def add_moderator_entry(self, model):
        moderator_entry = GenericRelation(ModeratorEntry)
        model.add_to_class('moderator_entry', moderator_entry)

        # need to flush fields names cache
        model._meta.add_field(moderator_entry)

    def remove_moderator_entry(self, model):
        del model.moderator_entry

    def get_related_models(self, model):
        related = []

        concrete_model = model._meta.concrete_model
        for field in concrete_model._meta.local_fields:
            if field.rel:
                related.append(field.rel.to)

        return related

moderator = Moderator()

default_app_config = 'moderator.app.ModeratorConfig'
