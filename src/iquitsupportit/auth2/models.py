from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import hashlib
import uuid


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
