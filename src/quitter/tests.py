from django.test import TestCase
from django.contrib.auth.models import User
import datetime
from quitter.models import Profile, Beneficiary
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.timezone import now
from django.core import mail
import re
from auth2.models import EmailAccount
import hashlib
import uuid


def create_default_profile():
    user = User.objects.create_user('Default user', 'default@bar.com', 'bar')
    beneficiary = Beneficiary.objects.create(quitter=user,
                                             name='My charity',
                                             url='http://mycharity.com',
                                             donate_url='http://mycharity.com/donate',
                                             banner=None,
                                             banner_font_theme='',
                                             banner_copyright='',
                                             logo=None)
    profile = Profile.objects.create(user=user,
                                     slug=settings.DEFAULT_PROFILE,
                                     quit_date=now(),
                                     cigarettes_per_day=10,
                                     pack_price=7,
                                     pack_size=20,
                                     donation_percentage=100,
                                     current_beneficiary=beneficiary,
                                     testimony='Write your testimony here!',
                                     video_embed_url=None,
                                     picture=None)

    return user


class ProfileTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        create_default_profile()

    def test_register_new_profile(self):
        path = reverse('signup')
        data = {'email': 'foo@bar.com'}
        response = self.client.post(path, data)

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Profile.objects.count(), 2)
        self.assertEqual(Beneficiary.objects.count(), 2)

        self.assertEqual(User.objects.filter(email='foo@bar.com').count(), 1)
        user = User.objects.get(email='foo@bar.com')
        self.assertEqual(user.profile.slug, 'foo')
        self.assertEqual(user.profile.current_beneficiary.name, 'My charity')
        self.assertNotEqual(user.profile.current_beneficiary.id,
                            Profile.objects.get(slug=settings.DEFAULT_PROFILE).current_beneficiary.id)
        self.assertEqual(mail.outbox[0].subject, 'Please confirm your signup')
        messages = [m for m in response.context['messages']]
        self.assertEqual(messages[0].message, "An email has been sent to foo@bar.com with a link to confirm your signup. Check your spam folder if you haven't received anything.")

    def test_register_twice(self):
        path = reverse('signup')
        data = {'email': 'foo@bar.com'}
        response = self.client.post(path, data)
        response = self.client.post(path, data)

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Profile.objects.count(), 2)
        self.assertEqual(Beneficiary.objects.count(), 2)

        self.assertEqual(mail.outbox[1].subject, 'Please confirm your signup')
        messages = [m for m in response.context['messages']]
        self.assertEqual(messages[0].message, "An email has been sent to foo@bar.com with a link to confirm your signup. Check your spam folder if you haven't received anything.")
        self.assertEqual(messages[1].message, "A new confirmation email has been sent. Check your spam folder if you haven't received it.")

    def test_confirm_registration(self):
        path = reverse('signup')
        data = {'email': 'foo@bar.com'}
        response = self.client.post(path, data)
        regex = re.compile(r'/signup/([\w-]+)/')
        result = regex.search(mail.outbox[0].body)
        token = result.group(1)

        path = reverse('confirm_signup', kwargs={'hash': token})
        response = self.client.post(path)

        self.assertIsNone(EmailAccount.objects.get(email=data['email']).hash)

    def test_register_twice_after_confirmation(self):
        path = reverse('signup')
        data = {'email': 'foo@bar.com'}
        response = self.client.post(path, data)

        self.assertEqual(len(mail.outbox), 1)

        regex = re.compile(r'/signup/([\w-]+)/')
        result = regex.search(mail.outbox[0].body)
        token = result.group(1)

        path = reverse('confirm_signup', kwargs={'hash': token})
        response = self.client.post(path)

        path = reverse('signup')
        response = self.client.post(path, data)

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Profile.objects.count(), 2)
        self.assertEqual(Beneficiary.objects.count(), 2)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, 'Please confirm your signup')

    def test_register_profile_from_pledger(self):
        pledger = User.objects.create_user(hashlib.sha256(str(uuid.uuid4())).hexdigest()[:30], 'pledger@bar.com', '!')
        pledger.set_unusable_password()
        pledger.save()

        path = reverse('signup')
        data = {'email': 'pledger@bar.com'}
        response = self.client.post(path, data)

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Profile.objects.count(), 2)
        self.assertEqual(Beneficiary.objects.count(), 2)
