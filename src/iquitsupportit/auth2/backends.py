from django.contrib.auth.models import User
import hashlib
from django.contrib.auth.backends import ModelBackend
from auth2.models import EmailAccount


class EmailBackend(ModelBackend):
    def authenticate(self, email=None, password=None, **kwargs):
        try:
            account = EmailAccount.objects.get(email=email)
            if account.user.check_password(password):
                return account.user
        except EmailAccount.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            User().set_password(password)


class TokenBackend(object):
    def authenticate(self, token=None):
        if token:
            try:
                account = EmailAccount.objects.get(hash=hashlib.sha1(token).hexdigest())
                account.hash = None
                account.save()
                return account.user
            except EmailAccount.DoesNotExist:
                pass

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
