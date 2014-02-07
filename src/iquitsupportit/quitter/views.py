from django.shortcuts import get_object_or_404, render_to_response
from quitter.models import Profile
from django.template.context import RequestContext
from supporter.forms import PledgeForm


def index(request, slug):
    profile = get_object_or_404(Profile, slug=slug)
    context = {}
    context['profile'] = profile
    context['form'] = PledgeForm()
    return render_to_response('index.html',
                              context,
                              context_instance=RequestContext(request))
