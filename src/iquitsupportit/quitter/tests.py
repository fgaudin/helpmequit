from django.test import TestCase
from django.contrib.auth.models import User
import datetime
from quitter.models import Profile


class QuitterTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('foo', 'foo@bar.com', 'bar')

    def test_duration(self):
        Profile.objects.create(user=self.user,
                               slug='foo',
                               quit_date=datetime.datetime.utcnow() - datetime.timedelta(3),
                               cigarettes_per_day=5,
                               pack_price=4.8,
                               pack_size=20)

        self.assertEqual(self.user.profile.duration().days, 3)

    def test_duration_str(self):
        Profile.objects.create(user=self.user,
                               slug='foo',
                               quit_date=datetime.datetime.utcnow() - datetime.timedelta(3),
                               cigarettes_per_day=5,
                               pack_price=4.8,
                               pack_size=20)

        self.assertEqual(self.user.profile.duration_str(), '3d 00:00')

    def test_amount_saved(self):
        Profile.objects.create(user=self.user,
                               slug='foo',
                               quit_date=datetime.datetime.utcnow() - datetime.timedelta(3),
                               cigarettes_per_day=5,
                               pack_price=4.8,
                               pack_size=20)

        self.assertEqual(self.user.profile.amount_saved(), 3.6)
