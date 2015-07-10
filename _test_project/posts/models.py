# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    text = models.TextField()

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return "%s pk=%s" % (self.title, self.pk)


class PostWithImage(Post):
    image = models.ImageField()
