from django.conf import settings


def settings_variables(request):
    return {'sitename': settings.SITENAME,
            'contact': settings.ADMINS[0]}
