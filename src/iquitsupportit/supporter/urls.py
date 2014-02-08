from django.conf.urls import patterns, url


urlpatterns = patterns('supporter.views',
    url(r'^(?P<beneficiary_id>\d+)/new/$', 'pledge_create', name='pledge_create'),
    url(r'^(?P<hash>[0-9a-f\-]+)/confirm/$', 'pledge_confirm', name='pledge_confirm'),
    url(r'^(?P<hash>[0-9a-f\-]+)/honor/$', 'pledge_honor', name='pledge_honor'),
)
