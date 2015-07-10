# -*- coding: utf-8 -*-

from django.contrib import admin

from moderator.admin import moderator, ModelModerator

from models import Post, PostWithImage

# Register your models here.
admin.site.register(Post)
admin.site.register(PostWithImage)

moderator.register(Post, ModelModerator)
moderator.register(PostWithImage, ModelModerator)
