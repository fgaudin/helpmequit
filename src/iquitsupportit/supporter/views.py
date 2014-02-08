from django.shortcuts import get_object_or_404, redirect
from quitter.models import Beneficiary
from supporter.forms import PledgeForm
from django.http.response import HttpResponseNotAllowed, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import json
from django.utils.translation import gettext as _
import uuid
from supporter.models import Pledge
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.transaction import commit_on_success
from django.core.mail import send_mail
from django.conf import settings


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
            user = User.objects.create_user(email, email, '!')
            user.set_unusable_password()

        pledge = form.save(commit=False)
        pledge.supporter = user
        pledge.beneficiary = beneficiary
        pledge.hash = uuid.uuid4()
        pledge.save()

        url = 'http://%s%s' % (request.get_host(),
                               reverse('pledge_confirm', kwargs={'hash': pledge.hash}))

        message = _("""Thank you! I really appreciate your support.\n\nYou
 pledged to donate $%(amount)d when I reach %(days)d days without smoking. Now, you
 need to confirm your pledge so we can send you a reminder and a link when I
 will reach this goal. Confirm: %(url)s""") % {'amount': pledge.amount,
                              'days': pledge.days,
                              'url': url}

        send_mail(_('Please confirm your pledge'), message, settings.DEFAULT_FROM_EMAIL,
                  [user.email], fail_silently=False)

        response_data = {'status': True,
                         'message': _('Thank you! Check your emails to confirm your pledge')}
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
