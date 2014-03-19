from requests_oauthlib.oauth2_session import OAuth2Session
from django.conf import settings
from django.http.response import HttpResponseRedirect
from requests_oauthlib.compliance_fixes.facebook import facebook_compliance_fix
from context_processors import settings_variables
from django.core.urlresolvers import reverse
import requests
from django.db.transaction import commit_on_success
from auth2.models import FacebookAccount
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
import logging

AUTHORIZATION_URL = 'https://www.facebook.com/dialog/oauth?scope=email'
TOKEN_URL = 'https://graph.facebook.com/oauth/access_token'
USER_URL = 'https://graph.facebook.com/me'

oauth2_session = None


def init_oauth2_session(request):
    oauth2_session = OAuth2Session(settings.FACEBOOK_CLIENT_ID,
            redirect_uri='%s%s' % ('https://xb999.gondor.co',
                                   reverse('facebook_complete')))
    oauth2_session = facebook_compliance_fix(oauth2_session)
    return oauth2_session


def facebook_login(request):
    oauth2_session = init_oauth2_session(request)
    authorization_url, state = oauth2_session.authorization_url(AUTHORIZATION_URL)
    request.session['oauth_state'] = state
    return HttpResponseRedirect(authorization_url)


def _fetch_token(request):
    oauth2_session = init_oauth2_session(request)
    redirect_response = request.build_absolute_uri()
    # TODO handle errors
    return oauth2_session.fetch_token(TOKEN_URL,
        client_secret=settings.FACEBOOK_CLIENT_SECRET,
        authorization_response=redirect_response)


def _get_user_data(token):
    response = requests.get(USER_URL, params={"access_token": token['access_token']})
    # TODO handle errors
    if response.status_code != 200:
        raise Exception

    json_response = response.json()

    json_response['token'] = token
    uid = json_response.get('id', '')
    data = {
        'email': json_response.get('email', ''),
        'first_name': json_response.get('first_name', ''),
        'last_name': json_response.get('last_name', ''),
        'social_data': json_response
    }
    return uid, data


@commit_on_success
def facebook_complete(request):
    if not request.GET.get('error'):
        token = _fetch_token(request)
        user_data = _get_user_data(token)

        account = FacebookAccount.objects.get_or_create_account(user_data)
        user = authenticate(uuid=account.uuid)
        if user:
            login(request, user)
            # trick for gondor.io
            # facebook redirect to https://xxxxxx.gondor.io
            # then we redirect to http://helpmequ.it
            return redirect('%s%s' % (settings_variables(request)['website_url'], reverse('me')))

    messages.error(request, _('You refused to signup with Facebook'))
    return redirect(reverse('home'))



