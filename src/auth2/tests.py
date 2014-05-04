from django.test.testcases import TestCase
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from auth2.models import EmailAccount, AlreadyExistsError


class EmailBackendTestCase(TestCase):
    def test_email_auth_success(self):
        user = User.objects.create_user('foo', 'foo@bar.com', 'test')
        account = EmailAccount.objects.create(user=user,
                                              email='foo2@bar.com',
                                              hash=None)

        loggedin_user = authenticate(email='foo@bar.com', password='test')
        self.assertIsNone(loggedin_user)
        loggedin_user = authenticate(email='foo2@bar.com', password='test')
        self.assertEqual(user, loggedin_user)

    def test_token_auth_success(self):
        account = EmailAccount.objects.create_account(email='foo2@bar.com',
                                                      hash='abcd')

        loggedin_user = authenticate(token='1234')
        self.assertIsNone(loggedin_user)
        loggedin_user = authenticate(token='abcd')
        self.assertEqual(account.user, loggedin_user)
        self.assertIsNone(EmailAccount.objects.get(pk=account.id).hash)


class EmailAccountTestCase(TestCase):
    def test_create_account(self):
        account = EmailAccount.objects.create_account('foo@bar.com', 'abcd')

        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertEqual(user.email, 'foo@bar.com')
        self.assertFalse(user.has_usable_password())
        self.assertEqual(user, account.user)

    def test_account_already_exists(self):
        account1 = EmailAccount.objects.create_account('foo@bar.com', 'abcd')
        with self.assertRaises(AlreadyExistsError):
            account2 = EmailAccount.objects.create_account('foo@bar.com', '1234')
