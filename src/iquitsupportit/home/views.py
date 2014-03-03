from django.shortcuts import render_to_response
from django.template.context import RequestContext
from quitter.models import Profile
from django.conf import settings
from quitter.forms import SignupForm, LoginForm
from django.utils.translation import ugettext as _, get_language


def index(request):
    try:
        featured_profile = Profile.objects.get(slug=settings.DEFAULT_I18N_PROFILES[get_language()])
    except:
        featured_profile = Profile.objects.get(slug=settings.DEFAULT_PROFILE)
    context = {
        'featured': featured_profile,
        'signup_link': '<a href="#" id="signup">%s</a>' % _('sign up'),
        'signup_form': SignupForm(),
        'login_link': '<a href="#" id="login">%s</a>' % _('log in'),
        'login_form': LoginForm()
    }
    return render_to_response('home/index.html',
                              context,
                              context_instance=RequestContext(request))
