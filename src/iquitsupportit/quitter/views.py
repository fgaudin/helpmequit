from django.shortcuts import get_object_or_404, render_to_response, redirect
from quitter.models import Profile
from django.template.context import RequestContext
from supporter.forms import PledgeForm
from quitter.forms import SignupForm, LoginForm, SetPasswordForm, ProfileForm, \
    UserForm
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
import uuid
from django.db.transaction import commit_on_success
from django.contrib.auth.decorators import login_required


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


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            create_profile = False
            user = None
            send_email = False
            profile = None
            hash = None
            try:
                user = User.objects.get(email=email)
                if user.has_usable_password():
                    messages.error(request, _("This email is already registered. If it's yours, use the 'forgot password' link."))
                else:
                    if user.profile:
                        send_email = True
                        profile = user.profile
                        hash = uuid.uuid4()
                        profile.set_hash(hash)
                        profile.save()
                        messages.info(request, _('A new confirmation email has been sent.'))
                    else:
                        # pledger who wants to create an account
                        create_profile = True
            except ObjectDoesNotExist:
                # new subscription
                user = User.objects.create_user(email, email, '!')
                user.set_unusable_password()
                user.save()
                create_profile = True

            if create_profile:
                # create profile
                hash = uuid.uuid4()
                profile = Profile.objects.create_profile(user, hash)
                send_email = True
                messages.info(request, _('You will receive an email shortly with a link to confirm your signup.'))

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
                text_content = render_to_string(template_text, context)
                html_content = render_to_string(template_html, context)

                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
        else:
            messages.error(request, _("Your email is not valid."))
    else:
            messages.error(request, _("Method not allowed."))

    return redirect(request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else 'home')


def confirm_signup(request, hash):
    user = authenticate(token=hash)
    if user is not None:
        auth_login(request, user)
    else:
        messages.error(request, _('Hash invalid'))

    return redirect(reverse('home'))


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(username=email, password=password)
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

    if request.method == 'POST':
        if request.POST.get('update_password'):
            password_form = SetPasswordForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, _('Password updated successfully'))
                return redirect(reverse('edit'))
        elif request.POST.get('update'):
            user_form = UserForm(request.POST, instance=request.user)
            profile_form = ProfileForm(request.POST, instance=request.user.profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, _('Your page has been updated successfully'))
                return redirect(reverse('user', kwargs={'slug': request.user.profile.slug}))

    context['password_form'] = password_form
    context['user_form'] = user_form
    context['profile_form'] = profile_form

    return render_to_response('edit.html',
                              context,
                              context_instance=RequestContext(request))
