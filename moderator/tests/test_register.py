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
from ..models import (
    MODERATION_STATUS_PENDING,
)
# from ..managers import ModeratorManager

from models import Model


class ModeratorTest(TestCase):
    def setUp(self):
        self.default_manager = Model.objects

    def tearDown(self):
        try:
            moderator.unregister(Model)
        except:
            pass

        Model.add_to_class('objects', self.default_manager)

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

    @mock.patch.object(moderator, 'disconnect_signals')
    def test_unregister_calls_disconnect_signals(self, m_disconnect):
        moderator._registered[Model] = None
        moderator.unregister(Model)

        m_disconnect.assert_called_with(Model)

    @mock.patch('moderator.signals.post_save.disconnect')
    def test_disconnects_signals(self, m_disconnect):
        moderator.disconnect_signals(Model)

        m_disconnect.assert_called_with(moderator.on_post_save, sender=Model)

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
        m_get.return_value = object
        moderator.update_managers(Model, ModeratorBase)

        self.assertEqual(Model.objects.__class__, object)

    def test_add_moderator_etry_field(self):
        moderator.add_moderator_entry(Model)

        self.assertTrue(hasattr(Model, 'moderator_entry'))

    def test_register_adds_moderator_entry_field(self):
        moderator.register(Model)

        self.assertTrue(hasattr(Model, 'moderator_entry'))

    def test_on_post_save_creates_moderatorentry(self):
        moderator.register(Model)

        model = Model.objects.create()
        self.assertTrue(hasattr(model, 'moderator_entry'))
        self.assertTrue(model.moderator_entry.all())

    def test_can_create_model_after_register(self):
        moderator.register(Model)

        model = Model()
        model.save()
        self.assertTrue(model)

        model = Model.objects.create()
        self.assertTrue(model)

    def test_can_filter_model_after_register(self):
        moderator.register(Model)

        model = Model()
        model.save()
        self.assertTrue(model)

        print(model.moderator_entry)

        models = Model.objects.filter(moderator_entry=MODERATION_STATUS_PENDING)
        self.assertIn(model, models)
