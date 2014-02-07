from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'quitter.views.index', {'slug': 'francois'}, name='home'),
    url(r'^pledge/', include('supporter.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
