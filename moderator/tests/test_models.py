# -*- coding: utf-8 -*-

from dictdiffer import diff

from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.test import TestCase

from ..models import (
    ModeratorEntry,
    # Changes,
)

from models import Model


class TestModeratorEntry(TestCase):
    def test_diff_saves_original_values(self):
        m = Model.objects.create(name='model first version')
        me = ModeratorEntry.objects.create(
            content_type=ContentType.objects.get_for_model(Model),
            object_id=m.pk
        )

        m.name = 'model second version'
        me.diff(m)

        values = serializers.serialize('python', [m])[0]
        self.assertEqual(me.original_values, values)

    def test_diff_creates_changes_record(self):
        m = Model.objects.create(name='model first version')
        me = ModeratorEntry.objects.create(
            content_type=ContentType.objects.get_for_model(Model),
            object_id=m.pk
        )

        m.name = 'model second version'
        m.save()

        me.diff()

        self.assertTrue(me.changes.all())

    def test_diff_fill_changes_diff(self):
        m = Model.objects.create(name='model first version')
        me = ModeratorEntry.objects.create(
            content_type=ContentType.objects.get_for_model(Model),
            object_id=m.pk
        )

        m.name = 'model second version'
        me.diff(m)

        changes = me.changes.all()[0]

        self.assertTrue(changes.diff)
        self.assertEqual(changes.diff, [
            ['change', 'fields.name', ['model first version', 'model second version']]
        ])
