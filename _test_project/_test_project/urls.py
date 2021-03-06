from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import moderator
moderator.autodiscover()

from moderator.admin import moderator

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', '_test_project.views.home', name='home'),
    # url(r'^_test_project/', include('_test_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^moderator/', include(moderator.urls)),
)
