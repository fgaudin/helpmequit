from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^signup/(?P<hash>[0-9a-f\-]+)/', 'quitter.views.confirm_signup', name="confirm_signup"),
    url(r'^signup/', 'quitter.views.signup', name="signup"),
    url(r'^login/', 'quitter.views.login', name="login"),
    url(r'^logout/', 'quitter.views.logout', name="logout"),
    url(r'^auth/', include('auth2.urls')),
    url(r'^me$', 'quitter.views.me', name='me'),
    url(r'^me/edit', 'quitter.views.edit', name="edit"),
    url(r'^u/(?P<slug>[\w\.]+)/$', 'quitter.views.index', name='user'),
    url(r'^b/(?P<id>\d+)/form/$', 'quitter.views.beneficiary_form', name='beneficiary_form'),
    url(r'^p/', include('supporter.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += i18n_patterns('',
    url(r'^$', 'home.views.index', name='home'),
)
