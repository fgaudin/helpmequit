from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import hashlib
import uuid
import re
from quitter.models import Profile


FIRSTNAME_REGEX = re.compile('(\w+)')


class EmailAccountManager(models.Manager):
    def associate(self, user, hash):
        account = self.create(user=user,
                              email=user.email,
                              hash=hashlib.sha1(str(hash)).hexdigest())
        return account

    def create_account(self, email, hash):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(hashlib.sha256(str(uuid.uuid4())).hexdigest()[:30], email, '!')
            match = FIRSTNAME_REGEX.search(user.email)
            if match:
                user.first_name = match.group().lower().capitalize()
                user.save()

        user.set_unusable_password()
        user.save()
        account = self.associate(user, hash)

        return account


class EmailAccount(models.Model):
    user = models.ForeignKey(User)
    email = models.EmailField(_('email address'), unique=True)
    hash = models.CharField(max_length=128, null=True, blank=True)

    objects = EmailAccountManager()

    def __unicode__(self):
        return u"%s" % self.email

    def set_hash(self, hash):
        self.hash = hashlib.sha1(str(hash)).hexdigest()


class FacebookAccountManager(models.Manager):
    def get_or_create_account(self, user_data):
        try:
            return self.get(uuid=user_data[0])
        except FacebookAccount.DoesNotExist as e:
            user = User.objects.create_user(hashlib.sha256(str(uuid.uuid4())).hexdigest()[:30], user_data[1]['email'], '!')
            user.first_name = user_data[1]['first_name'].lower().capitalize()
            user.set_unusable_password()
            user.save()

            account = FacebookAccount(user=user,
                                      uuid=user_data[0])
            account.save()

            Profile.objects.create_profile(user)

            return account


class FacebookAccount(models.Model):
    user = models.ForeignKey(User)
    uuid = models.CharField(max_length=255, unique=True)

    objects = FacebookAccountManager()
