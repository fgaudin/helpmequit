from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'quitter.views.index', {'slug': 'francois'}, name='home'),
    url(r'^signup/(?P<hash>[0-9a-f\-]+)/', 'quitter.views.confirm_signup', name="confirm_signup"),
    url(r'^signup/', 'quitter.views.signup', name="signup"),
    url(r'^login/', 'quitter.views.login', name="login"),
    url(r'^logout/', 'quitter.views.logout', name="logout"),
    url(r'^me$', 'quitter.views.me', name='me'),
    url(r'^me/edit', 'quitter.views.edit', name="edit"),
    url(r'^u/(?P<slug>[\w\d\.]+)/$', 'quitter.views.index', name='user'),
    url(r'^b/(?P<id>\d+)/form/$', 'quitter.views.beneficiary_form', name='beneficiary_form'),
    url(r'^p/', include('supporter.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
