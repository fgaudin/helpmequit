from django.test import TestCase
import datetime
from django.contrib.auth.models import User
from quitter.models import Profile
from supporter.models import Pledge


class SupporterTestCase(TestCase):
    def test_pledge_date_reached(self):
        quitter = User.objects.create_user('foo', 'foo@bar.com', 'bar')
        Profile.objects.create(user=quitter,
                               slug='foo',
                               quit_date=datetime.datetime.utcnow() - datetime.timedelta(3),
                               cigarettes_per_day=5,
                               pack_price=4.8,
                               pack_size=20)

        supporter = User.objects.create_user('foo2', 'foo2@bar.com', 'bar')
        pledge1 = Pledge.objects.create(user=supporter,
                                        quitter=quitter,
                                        days=4,
                                        amount=10)

        self.assertFalse(pledge1.reached())

        pledge2 = Pledge.objects.create(user=supporter,
                                        quitter=quitter,
                                        days=2,
                                        amount=10)

        self.assertTrue(pledge2.reached())

        pledge3 = Pledge.objects.create(user=supporter,
                                        quitter=quitter,
                                        days=3,
                                        amount=10)

        self.assertTrue(pledge3.reached())
