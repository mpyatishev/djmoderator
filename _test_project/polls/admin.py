# -*- coding: utf-8 -*-

from django.contrib import admin

from moderator.admin import moderator, ModelModerator

from models import Poll

# Register your models here.
admin.site.register(Poll)

moderator.register(Poll, ModelModerator)
