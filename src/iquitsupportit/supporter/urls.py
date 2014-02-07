from django.conf.urls import patterns, url


urlpatterns = patterns('supporter.views',
    url(r'^(?P<beneficiary_id>\d+)/new/$', 'create', name='pledge'),
)
