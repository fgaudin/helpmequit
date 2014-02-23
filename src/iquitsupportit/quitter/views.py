from django.shortcuts import get_object_or_404, render_to_response, redirect
from quitter.models import Profile, Beneficiary
from django.template.context import RequestContext
from supporter.forms import PledgeForm
from quitter.forms import SignupForm, LoginForm, SetPasswordForm, ProfileForm, \
    UserForm, BeneficiaryForm
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
import uuid
from django.db.transaction import commit_on_success
from django.contrib.auth.decorators import login_required
import requests
from bs4 import BeautifulSoup
from auth2.models import EmailAccount


def index(request, slug=None):
    if slug:
        profile = get_object_or_404(Profile, slug=slug)
    else:
        if request.user.is_authenticated():
            profile = request.user.profile
        else:
            redirect(reverse('home'))

    context = {}
    context['profile'] = profile
    context['form'] = PledgeForm()
    context['signup_form'] = SignupForm()
    context['login_form'] = LoginForm()
    return render_to_response('index.html',
                              context,
                              context_instance=RequestContext(request))


@login_required
def me(request):
    return redirect(reverse('user', kwargs={'slug': request.user.profile.slug}))


@commit_on_success
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = None
            send_email = False
            account = None
            hash = uuid.uuid4()
            try:
                account = EmailAccount.objects.get(email=email)
                user = account.user
                if user.has_usable_password():
                    messages.error(request, _("This email is already registered. If it's yours, use the 'forgot password' link."))
                else:
                    if user.profile:
                        send_email = True
                        account.set_hash(hash)
                        account.save()
                        messages.info(request, _("A new confirmation email has been sent. Check your spam folder if you haven't received it."))
            except EmailAccount.DoesNotExist:
                # new subscription
                account = EmailAccount.objects.create_account(email, hash)
                user = account.user

                # create profile
                Profile.objects.create_profile(user)
                send_email = True
                messages.info(request, _("An email has been sent to %s with a link to confirm your signup. Check your spam folder if you haven't received anything.") % (user.email))

            if send_email:
                template_html = 'signup/email.html'
                template_text = 'signup/email.txt'
                subject = _(u"Please confirm your signup")
                to = user.email
                from_email = settings.DEFAULT_FROM_EMAIL
                url = 'http://%s%s' % (request.get_host(),
                                       reverse('confirm_signup', kwargs={'hash': hash}))

                context = {'url': url,
                           'signature': settings.EMAIL_SIGNATURE}
                text_content = render_to_string(template_text,
                                                context,
                                                context_instance=RequestContext(request))
                html_content = render_to_string(template_html,
                                                context,
                                                context_instance=RequestContext(request))

                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
        else:
            messages.error(request, _("Your email is not valid."))
    else:
            messages.error(request, _("Method not allowed."))

    return redirect(request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else 'home')


@commit_on_success
def confirm_signup(request, hash):
    user = authenticate(token=hash)
    if user is not None:
        auth_login(request, user)
        return redirect(reverse('edit'))
    else:
        messages.error(request, _('Hash invalid'))

    return redirect(reverse('home'))


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(email=email, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect(reverse('user', kwargs={'slug': request.user.profile.slug}))

        messages.error(request, _('Email and/or password invalid'))
    else:
        messages.error(request, _('Method not allowed'))

    return redirect(request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else 'home')


def logout(request):
    auth_logout(request)
    return redirect(reverse('home'))


@login_required
@commit_on_success
def edit(request):
    context = {}

    password_form = SetPasswordForm(user=request.user)
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    profile_form.fields['current_beneficiary'].queryset = Beneficiary.objects.filter(quitter_id=request.user.id)
    beneficiary_form = BeneficiaryForm(prefix='existing', instance=request.user.profile.current_beneficiary)
    new_beneficiary_form = BeneficiaryForm(prefix='new')

    if request.method == 'POST':
        if request.POST.get('update_password'):
            password_form = SetPasswordForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, _('Password updated successfully'))
                return redirect(reverse('edit'))
        elif request.POST.get('update'):
            user_form = UserForm(request.POST, instance=request.user)
            profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

            if user_form.is_valid() and profile_form.is_valid():
                beneficiary_form = BeneficiaryForm(request.POST, request.FILES, prefix='existing', instance=request.user.profile.current_beneficiary)
                new_beneficiary_form = BeneficiaryForm(request.POST, request.FILES, prefix='new')

                user_form.save()
                profile = profile_form.save(commit=False)

                if new_beneficiary_form.is_valid():
                    beneficiary = new_beneficiary_form.save(commit=False)
                    beneficiary.quitter = request.user
                    beneficiary.save()
                    profile.current_beneficiary = beneficiary
                elif beneficiary_form.is_valid():
                    beneficiary = beneficiary_form.save(commit=False)
                    beneficiary.id = profile.current_beneficiary_id
                    beneficiary.save()

                if profile_form.cleaned_data['video_url']:
                    response = requests.get(profile_form.cleaned_data['video_url'])
                    soup = BeautifulSoup(response.text, 'lxml')
                    tag = soup.find('meta', {'name': 'twitter:player'})
                    if tag and 'content' in tag.attrs:
                        profile.video_embed_url = tag.attrs['content']
                    elif tag and 'value' in tag.attrs:
                        profile.video_embed_url = tag.attrs['value']
                    else:
                        messages.warning(request, _("The url doesn't contain any video"))
                    if profile.video_embed_url:
                        profile.picture = None
                elif profile.picture:
                    profile.video_embed_url = None

                profile.save()
                messages.success(request, _('Your page has been updated successfully'))
                return redirect(reverse('user', kwargs={'slug': request.user.profile.slug}))

    context['password_form'] = password_form
    context['user_form'] = user_form
    context['profile_form'] = profile_form
    context['beneficiary_form'] = beneficiary_form
    context['new_beneficiary_form'] = new_beneficiary_form

    return render_to_response('edit.html',
                              context,
                              context_instance=RequestContext(request))


@login_required
def beneficiary_form(request, id):
    beneficiary = get_object_or_404(Beneficiary, pk=id, quitter=request.user)
    beneficiary_form = BeneficiaryForm(prefix='existing', instance=beneficiary)
    return render_to_response('beneficiary_form.html',
                              {'form': beneficiary_form},
                              context_instance=RequestContext(request))
