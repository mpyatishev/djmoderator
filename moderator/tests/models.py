# -*- coding: utf-8 -*-

from django.db import models


class Model(models.Model):
    name = models.CharField(max_length=255)
