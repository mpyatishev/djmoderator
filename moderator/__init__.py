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
        self._relations = {}
        self._default_managers = {}

    def register(self, models_list, moderator=None, with_related=False):
        if isinstance(models_list, ModelBase):
            models_list = [models_list]

        related = []
        if with_related:
            for model in models_list:
                self._relations[model] = self.get_related_models(model)
                related += [_ for _, attr in self._relations[model]]
            models_list += related

        moderator = moderator or ModeratorBase

        for model in models_list:
            if model not in self._registered:
                self._registered[model] = moderator
                self.add_moderator_entry(model)
                self.update_managers(model, moderator)
                self.init_signals(model)
            elif model not in related:
                raise AlredyRegistered('Model %s alredy registered with %s'
                                       % (model, self._registered[model]))

    def unregister(self, models_list):
        if isinstance(models_list, ModelBase):
            models_list = [models_list]

        related = []
        for model in models_list:
            if model in self._relations:
                related += [_ for _, attr in self._relations[model]]
                del self._relations[model]
        models_list += related

        for model in models_list:
            if model in self._registered:
                del self._registered[model]
                self.disconnect_signals(model)
                self.remove_moderator_entry(model)
                self.make_old_managers(model)
            elif model not in related:
                raise NotRegistered('Model %s not registered' % model)

    def init_signals(self, model):
        signals.post_save.connect(self.on_post_save, sender=model, weak=False)

    def disconnect_signals(self, model):
        signals.post_save.disconnect(self.on_post_save, sender=model)

    def on_post_save(self, sender, instance, **kwargs):
        self.moderate(sender, instance)

        if sender in self._relations:
            for model, field in self._relations[sender]:
                related_instance = getattr(instance, field)

                if 'ManyRelatedManager' == related_instance.__class__.__name__:
                    for inst in related_instance.all():
                        self.moderate(model, inst, diff=False)
                else:
                    self.moderate(model, related_instance, diff=False)

    def moderate(self, model, instance, diff=True):
        me, created = ModeratorEntry.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(model),
            object_id=instance.pk
        )

        if not created:
            if diff: me.diff()
            me.moderation_status = MODERATION_STATUS_PENDING
            me.save()

    def update_managers(self, model, moderator):
        if model not in self._default_managers:
            self._default_managers[model] = {}

        managers = self._default_managers[model]

        for manager_name in moderator.managers:
            if hasattr(model, manager_name):
                manager = getattr(model, manager_name)
                if manager_name not in managers:
                    managers[manager_name] = manager
                new_manager = ModeratorManagerFactory.get(bases=manager.__class__)
                model.add_to_class(manager_name, new_manager())

    def make_old_managers(self, model):
        if model not in self._default_managers:
            return

        managers = self._default_managers[model]
        for manager_name in managers:
            manager = managers[manager_name]
            model.add_to_class(manager_name, manager)

    def add_moderator_entry(self, model):
        moderator_entry = GenericRelation(ModeratorEntry)
        model.add_to_class('moderator_entry', moderator_entry)

        # need to flush fields names cache
        # model._meta.add_field(moderator_entry)

        # another method of flushing names cache
        if hasattr(model._meta, '_name_map'):
            del model._meta._name_map
        if hasattr(self, '_field_cache'):
            del self._field_cache
            del self._field_name_cache

    def remove_moderator_entry(self, model):
        del model.moderator_entry

    def get_related_models(self, model):
        related = []

        concrete_model = model._meta.concrete_model
        # foreign key
        for field in concrete_model._meta.local_fields:
            if field.rel and field.rel.to not in related:
                related.append((field.rel.to, field.name))

        # m2m
        for field in concrete_model._meta.local_many_to_many:
            if field.rel and field.rel.to not in related:
                related.append((field.rel.to, field.name))

        # reverse foreign key
        for attr in dir(model):
            model_attr = getattr(model, attr)
            if hasattr(model_attr, 'related'):
                foreign = model_attr.related.model
                if foreign not in related:
                    related.append((foreign, attr))

        return related

moderator = Moderator()

default_app_config = 'moderator.app.ModeratorConfig'
