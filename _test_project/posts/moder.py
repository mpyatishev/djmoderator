# -*- coding: utf-8 -*-

from moderator import moderator

from models import Post, PostWithImage

moderator.register(Post)
moderator.register(PostWithImage)
