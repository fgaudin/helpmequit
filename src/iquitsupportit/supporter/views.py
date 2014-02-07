from django.shortcuts import get_object_or_404
from quitter.models import Beneficiary
from supporter.forms import PledgeForm
from django.http.response import HttpResponseNotAllowed, HttpResponse
from supporter.models import Pledge
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


@csrf_exempt
def create(request, beneficiary_id):
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
        pledge.save()

    return HttpResponse('test')
