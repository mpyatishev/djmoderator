# -*- coding: utf-8 -*-

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from django.test import TestCase

from ..managers import ModeratorManagerFactory, ModeratorManager
from ..models import ModeratorEntry

# from models import Model


class ModelLocal(models.Model):
    pass


class TestsModeratorManagerFactory(TestCase):
    def test_get_manager_with_bases(self):
        model_manager = ModelLocal.objects.__class__

        manager = ModeratorManagerFactory.get(bases=model_manager)()

        self.assertIsInstance(manager, model_manager)


class TestModeratorManager(TestCase):
    def setUp(self):
        self.default_manager = ModelLocal.objects

        manager = ModeratorManagerFactory.get(bases=self.default_manager.__class__)
        moderator_entry = GenericRelation(ModeratorEntry)
        ModelLocal.add_to_class('objects', manager())
        ModelLocal.add_to_class('moderator_entry', moderator_entry)

    def tearDown(self):
        ModelLocal.add_to_class('objects', self.default_manager)

        del ModelLocal.moderator_entry

    def test_get_queryset(self):
        self.assertIn('moderation_status', str(ModelLocal.objects.get_queryset().query))
