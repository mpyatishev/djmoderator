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
    MODERATION_STATUS_APPROVED,
    MODERATION_STATUS_PENDING,
)

from models import Model, ModelFK, ModelM2M


class ModeratorTest(TestCase):
    def setUp(self):
        self.default_manager = Model.objects

    def tearDown(self):
        for m in (Model, ModelFK, ModelM2M):
            try:
                moderator.unregister(m)
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
    @mock.patch.object(moderator, 'remove_moderator_entry')
    def test_unregister_calls_disconnect_signals(self, m_remove, m_disconnect):
        moderator._registered[Model] = None
        moderator.unregister(Model)

        m_disconnect.assert_called_with(Model)

    def test_unregister_removes_moderator_entry(self):
        moderator.register(Model)
        moderator.unregister(Model)

        self.assertFalse(hasattr(Model, 'moderator_entry'))

        fields = []
        for field in Model._meta.fields:
            fields.append(field.name)
        self.assertNotIn('moderator_entry', fields)

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

        models = Model.objects.unmoderated()
        self.assertIn(model, models)

    @mock.patch.object(moderator, 'init_signals')
    @mock.patch.object(moderator, 'update_managers')
    @mock.patch.object(moderator, 'add_moderator_entry')
    def test_register_related_models(self, m_add_moderator_entry,
                                     m_update_managers, m_init_signals):
        moderator.register(ModelFK, with_related=True)

        self.assertIn(Model, moderator._registered)

        m_init_signals.assert_called_with(Model)
        m_update_managers.assert_called_with(Model, ModeratorBase)
        m_add_moderator_entry.assert_called_with(Model)

    def test_get_related_models_by_fk(self):
        related = moderator.get_related_models(ModelFK)

        self.assertIn(Model, related)

    def test_get_related_models_by_reverse_fk(self):
        related = moderator.get_related_models(Model)

        self.assertIn(ModelFK, related)

    def test_get_related_models_m2m(self):
        related = moderator.get_related_models(ModelM2M)

        self.assertIn(Model, related)

    def test_register_model_m2m(self):
        moderator.register(ModelM2M, with_related=True)

        self.assertIn(ModelM2M, moderator._registered)
        self.assertIn(Model, moderator._registered)

    def test_unregister_model_m2m(self):
        moderator.register(ModelM2M, with_related=True)
        moderator.unregister(ModelM2M)

        self.assertNotIn(ModelM2M, moderator._registered)
        self.assertNotIn(Model, moderator._registered)

    def test_on_post_save_changes_moderation_status_on_related(self):
        moderator.register(ModelFK, with_related=True)

        model = Model.objects.create(name='model')
        me = model.moderator_entry.all()[0]
        me.moderation_status = MODERATION_STATUS_APPROVED
        me.save()
        self.assertNotEqual(me.moderation_status, MODERATION_STATUS_PENDING)

        modelfk = ModelFK.objects.create(name='first', parent=model)
        me = model.moderator_entry.all()[0]
        self.assertEqual(me.moderation_status, MODERATION_STATUS_PENDING)

        me.moderation_status = MODERATION_STATUS_APPROVED
        me.save()

        me_modelfk = modelfk.moderator_entry.all()[0]
        me_modelfk.moderation_status = MODERATION_STATUS_APPROVED
        me_modelfk.save()

        modelfk.name = 'second'
        modelfk.save()
        me = model.moderator_entry.all()[0]
        self.assertEqual(me.moderation_status, MODERATION_STATUS_PENDING)

    def test_on_post_save_changes_moderation_status_on_related_m2m(self):
        moderator.register(ModelM2M, with_related=True)

        model = Model.objects.create(name='model')
        me = model.moderator_entry.all()[0]
        me.moderation_status = MODERATION_STATUS_APPROVED
        me.save()
        self.assertNotEqual(me.moderation_status, MODERATION_STATUS_PENDING)

        modelm2m = ModelM2M.objects.create(name='first')
        modelm2m.first.add(model)
        modelm2m.save()
        me = model.moderator_entry.all()[0]
        self.assertEqual(me.moderation_status, MODERATION_STATUS_PENDING)

        me.moderation_status = MODERATION_STATUS_APPROVED
        me.save()

        me_modelm2m = modelm2m.moderator_entry.all()[0]
        me_modelm2m.moderation_status = MODERATION_STATUS_APPROVED
        me_modelm2m.save()

        modelm2m.name = 'second'
        modelm2m.save()
        me = model.moderator_entry.all()[0]
        self.assertEqual(me.moderation_status, MODERATION_STATUS_PENDING)
