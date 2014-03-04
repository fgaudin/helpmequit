from django.shortcuts import get_object_or_404, redirect
from quitter.models import Beneficiary
from supporter.forms import PledgeForm
from django.http.response import HttpResponseNotAllowed, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import json
from django.utils.translation import ugettext as _
import uuid
from supporter.models import Pledge
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.transaction import commit_on_success
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives
from django.template.context import RequestContext
import hashlib


@csrf_exempt
@commit_on_success
def pledge_create(request, beneficiary_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    beneficiary = get_object_or_404(Beneficiary, pk=beneficiary_id)
    form = PledgeForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            user = User.objects.create_user(hashlib.sha256(str(uuid.uuid4())).hexdigest()[:30], email, '!')
            user.set_unusable_password()
            user.save()

        pledge = form.save(commit=False)
        pledge.supporter = user
        pledge.beneficiary = beneficiary
        pledge.hash = uuid.uuid4()
        pledge.save()

        template_html = 'email/confirm.html'
        template_text = 'email/confirm.txt'
        subject = _(u"Please confirm your pledge")
        to = user.email
        from_email = settings.DEFAULT_FROM_EMAIL
        url = 'http://%s%s' % (request.get_host(),
                               reverse('pledge_confirm', kwargs={'hash': pledge.hash}))

        context = {'amount': pledge.amount,
                   'days': pledge.days,
                   'url': url,
                   'quitter': pledge.beneficiary.quitter}
        text_content = render_to_string(template_text,
                                        context,
                                        context_instance=RequestContext(request))
        html_content = render_to_string(template_html,
                                        context,
                                        context_instance=RequestContext(request))

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        response_data = {'status': True,
                         'message': _("Thank you! Check your <strong>emails</strong> to confirm your pledge. Check your spam folder too if you haven't received it.")}
    else:
        response_data = {'status': False,
                         'errors': form.errors}

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def pledge_confirm(request, hash):
    pledge = get_object_or_404(Pledge, hash=hash)
    pledge.confirmed = True
    pledge.save()

    messages.success(request, _('Thank you! Your pledge has been confirmed.'))

    return redirect(reverse('home'))


def pledge_honor(request, hash):
    pledge = get_object_or_404(Pledge, hash=hash)
    pledge.honored = True
    pledge.save()

    messages.success(request, _('Thank you! Your donation has been recorded.'))

    return redirect(reverse('home'))
