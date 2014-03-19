from django.conf.urls import patterns, url


urlpatterns = patterns('auth2.views',
    url(r'^facebook/login$', 'facebook_login', name='facebook_login'),
    url(r'^facebook/complete', 'facebook_complete', name='facebook_complete'),
)
