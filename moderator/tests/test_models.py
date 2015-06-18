# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from ..models import (
    ModeratorEntry,
    # Changes,
)

from models import Model


class TestModeratorEntry(TestCase):
    def test_diff(self):
        m = Model.objects.create(name='model first version')
        me = ModeratorEntry.objects.create(
            content_type=ContentType.objects.get_for_model(Model),
            object_id=m.pk
        )

        m.name = 'model second version'
        m.save()

        me.diff()

        self.assertTrue(me.changes.all())
        self.assertEqual(me.original_values, {'name': 'model second version'})
