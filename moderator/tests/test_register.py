# -*- coding: utf-8 -*-

import mock

from django.test import TestCase

from .. import (
    moderator,
    ModeratorBase,

    ModeratorManagerFactory,

    AlredyRegistered,
    NotRegistered,
)
from ..managers import ModeratorManager
from models import Model


class ModeratorTest(TestCase):
    def setUp(self):
        self.default_manager = Model.objects

    def tearDown(self):
        if Model in moderator._registered:
            moderator.unregister(Model)
            Model.objects = self.default_manager

    def test_register_adds_model_to_dict(self):
        moderator.register(Model)
        self.assertIn(Model, moderator._registered)

    @mock.patch.object(moderator, 'init_signals')
    def test_register_calls_init_signals_for_model(self, m_init_signals):
        moderator.register(Model)

        m_init_signals.assert_called_with(Model)

    def test_register_raises_alredyregistered(self):
        moderator.register(Model)

        with self.assertRaises(AlredyRegistered):
            moderator.register(Model)

    def test_unregister_raises_notregistered(self):
        with self.assertRaises(NotRegistered):
            moderator.unregister(Model)

    @mock.patch.object(moderator, 'update_managers')
    def test_register_calls_update_managers_for_model(self, m_update_managers):
        moderator.register(Model)

        m_update_managers.assert_called_with(Model, ModeratorBase)

    @mock.patch.object(ModeratorManagerFactory, 'get')
    def test_update_managers_calls_moderatormanger(self, m_get):
        moderator.update_managers(Model, ModeratorBase)

        manager = Model.objects.__class__

        m_get.assert_called_with(bases=manager)

    @mock.patch.object(ModeratorManagerFactory, 'get')
    def test_update_managers_adds_manager_to_model(self, m_get):
        m_get.return_value = str
        moderator.update_managers(Model, ModeratorBase)

        self.assertEqual(Model.objects.__class__, str)
