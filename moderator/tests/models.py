# -*- coding: utf-8 -*-

from django.db import models


class Model(models.Model):
    name = models.CharField(max_length=255)


class ModelFK(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(Model, related_name="modelfk")


class ModelM2M(models.Model):
    name = models.CharField(max_length=255)
    first = models.ManyToManyField(Model, related_name='second')
