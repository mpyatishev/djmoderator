# -*- coding: utf-8 -*-

import json

from dictdiffer import diff

from django import template

register = template.Library()


@register.inclusion_tag('templatetags/moderator/diff.html')
def show_changes(obj):
    me = obj.moderator_entry.first()
    changes = me.get_changes()
    context = {
        'object': obj
    }

    if changes:
        for action, field, values in changes.diff:
            if action not in context:
                context[action] = []
            field_name = field.split('.')[-1]
            obj_field = obj._meta.get_field(field_name)
            context[action].append((obj_field, values))
    else:
        context['add'] = []
        for row in diff({}, me.original_values):
            for col, values in row[2]:
                if col == 'fields':
                    for field_name, value in values.items():
                        obj_field = obj._meta.get_field(field_name)
                        context['add'].append((obj_field, value))

    return context
