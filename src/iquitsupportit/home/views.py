from django.shortcuts import render_to_response
from django.template.context import RequestContext
from quitter.models import Profile
from django.conf import settings
from quitter.forms import SignupForm


def index(request):
    context = {
        'featured': Profile.objects.get(slug=settings.DEFAULT_PROFILE),
        'signup_form': SignupForm()
    }
    return render_to_response('home/index.html',
                              context,
                              context_instance=RequestContext(request))
