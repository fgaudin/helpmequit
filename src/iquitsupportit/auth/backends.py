from django.contrib.auth.models import User
import hashlib


class TokenBackend(object):
    def authenticate(self, token=None):
        if token:
            try:
                user = User.objects.get(profile__hash=hashlib.sha1(token).hexdigest())
                user.hash = None
                user.save()
                return user
            except User.DoesNotExist:
                return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
