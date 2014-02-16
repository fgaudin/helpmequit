from django.conf import settings


def settings_variables(request):
    return {'sitename': settings.SITENAME,
            'contact': settings.ADMINS[0],
            'signature': settings.EMAIL_SIGNATURE,
            'website_url': "http://%s" % settings.ALLOWED_HOSTS[0].lstrip('.')}
