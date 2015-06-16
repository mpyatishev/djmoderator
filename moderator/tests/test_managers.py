# -*- coding: utf-8 -*-

from django.test import TestCase

from ..managers import ModeratorManagerFactory

from models import Model


class TestsModeratorManagerFactory(TestCase):
    def test_get_manager_with_bases(self):
        model_manager = Model.objects.__class__

        manager = ModeratorManagerFactory.get(bases=model_manager)()

        self.assertIsInstance(manager, model_manager)
