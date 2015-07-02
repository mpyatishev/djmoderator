# -*- coding: utf-8 -*-

import json

from django import forms
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.options import ModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.http import (
    Http404,
    HttpResponse,
)
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from models import (
    MODERATION_STATUS_APPROVED,
    MODERATION_STATUS_PENDING,
    MODERATION_STATUS_REJECTED,
)


class ModeratedObject:
    pass


class ModeratorSite(AdminSite):
    index_template = 'moderator/index.html'
    list_template = 'moderator/list.html'

    def __init__(self, name='moderator', app_name='modeartor'):
        super(ModeratorSite, self).__init__(name, app_name)

    def has_permission(self, request):
        user = request.user

        if user.is_active and (user.is_superuser or user.is_moderator):
            return True

        return super(ModeratorSite, self).has_permission(request)

    def get_urls(self):
        from django.conf.urls import url, patterns, include

        # Add in each model's views, and create a list of valid URLS for the
        # app_index
        valid_app_labels = []
        for model, model_admin in six.iteritems(self._registry):
            urlpatterns = patterns(
                '',
                url(r'^%s/%s/pending/' % (model._meta.app_label, model._meta.model_name),
                    self.moderate_list, name='pending-list',
                    kwargs={'status': MODERATION_STATUS_PENDING, 'model': model}),
                url(r'^%s/%s/approved/' % (model._meta.app_label, model._meta.model_name),
                    self.moderate_list, name='approved-list',
                    kwargs={'status': MODERATION_STATUS_APPROVED, 'model': model}),
                url(r'^%s/%s/rejected/' % (model._meta.app_label, model._meta.model_name),
                    self.moderate_list, name='rejected-list',
                    kwargs={'status': MODERATION_STATUS_REJECTED, 'model': model}),
                url(r'^%s/%s/' % (model._meta.app_label, model._meta.model_name),
                    include(model_admin.urls))
            )
            if model._meta.app_label not in valid_app_labels:
                valid_app_labels.append(model._meta.app_label)

        urlpatterns += super(ModeratorSite, self).get_urls()

        return urlpatterns

    @never_cache
    def index(self, request, extra_context=None):

        context = {'apps': {}}
        for model, model_admin in six.iteritems(self._registry):
            approved = self.get_moderated_queryset(MODERATION_STATUS_APPROVED, model)\
                .count()
            rejected = self.get_moderated_queryset(MODERATION_STATUS_REJECTED, model)\
                .count()
            pending = self.get_moderated_queryset(MODERATION_STATUS_PENDING, model)\
                .count()

            if model._meta.app_label not in context['apps']:
                context['apps'][model._meta.app_label] = {}

            context['apps'][model._meta.app_label].update({
                model._meta.model_name: {
                    'approved': approved,
                    'rejected': rejected,
                    'pending': pending,
                }
            })

        return TemplateResponse(request, self.index_template, context)

    def get_moderated_queryset(self, status, model):
        return ModeratedObject.objects.filter(moderation_status=status,
                                              content_type=ContentType
                                              .objects.get_for_model(model))

    def moderate_list(self, request, *args, **kwargs):
        status = kwargs.get('status', None)
        model = kwargs.get('model', None)

        if status is None or model is None:
            return Http404

        context = {
            'models': self.get_moderated_queryset(status, model)
        }

        return TemplateResponse(request, self.list_template, context)


moderator = ModeratorSite()


class ModerateForm(forms.Form):
    reason = forms.CharField(required=False)
    approved = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super(ModerateForm, self).clean()

        if not cleaned_data.get('approved', False) and not cleaned_data.get('reason'):
            msg = _('It is necessary to specify the reason, if the Place is rejected')
            self.add_error('reason', msg)
            raise forms.ValidationError(msg)
        return cleaned_data


class ModelModerator(ModelAdmin):
    moderate_template = 'moderate.html'
    moderate_form = ModerateForm

    def get_urls(self):
        from django.conf.urls import patterns, url

        info = self.model._meta
        urlpatterns = patterns(
            '',
            url(r'^(?P<pk>\d+)/$', self.moderate, name='moderate-%s' % info.model_name)
        )

        return urlpatterns

    def get_context_data(self, *args, **kwargs):
        return {}

    def render_to_json_response(self, context, **kwargs):
        context = json.dumps(context)
        kwargs['content_type'] = 'application/json'
        return HttpResponse(context, **kwargs)

    def moderate(self, request, *args, **kwargs):
        if request.is_ajax():
            form = self.moderate_form(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                obj = self.get_object(request, kwargs.get('pk'))
                if data.get('approved', False):
                    obj.moderated_object.approve(moderated_by=request.user,
                                                 reason=data.get('reason', ''))
                else:
                    obj.moderated_object.reject(moderated_by=request.user,
                                                reason=data.get('reason', ''))
                return self.render_to_json_response('OK')
            else:
                return self.render_to_json_response(form.errors, status=400)
        else:
            context = self.get_context_data()

        obj = self.get_object(request, kwargs.get('pk'))

        return TemplateResponse(request, self.moderate_template, context)
