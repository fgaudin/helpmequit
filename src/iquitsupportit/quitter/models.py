from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models.aggregates import Sum
from django.conf import settings
import hashlib
from django.utils.translation import gettext_lazy as _


class ProfileManager(models.Manager):
    def create_profile(self, user, hash):
        default_profile = Profile.objects.get(slug=settings.DEFAULT_PROFILE)
        default_beneficiary = default_profile.current_beneficiary
        beneficiary = default_beneficiary.clone(user)

        return self.create(user=user,
                           slug=user.email,
                           quit_date=now(),
                           cigarettes_per_day=10,
                           pack_price=7,
                           pack_size=20,
                           donation_percentage=100,
                           current_beneficiary=beneficiary,
                           testimony='Lorem ipsum',
                           video_snippet='test',
                           hash=hashlib.sha1(str(hash)).hexdigest())


class Profile(models.Model):
    user = models.OneToOneField(User)
    slug = models.CharField(max_length=255, unique=True)
    quit_date = models.DateTimeField()
    cigarettes_per_day = models.PositiveIntegerField()
    pack_price = models.DecimalField(max_digits=5, decimal_places=2)
    pack_size = models.PositiveIntegerField()
    donation_percentage = models.PositiveIntegerField(default=100)
    current_beneficiary = models.ForeignKey('Beneficiary')
    testimony = models.TextField()
    hash = models.CharField(max_length=128, null=True, blank=True)
    video_embed_url = models.URLField(null=True, blank=True)
    picture = models.ImageField(upload_to='u/pic', null=True, blank=True)

    objects = ProfileManager()

    def __unicode__(self):
        return self.user.__unicode__()

    def duration(self):
        return now() - self.quit_date

    def duration_in_sec(self):
        duration = self.duration()
        return duration.days * 86400 + duration.seconds

    def duration_str(self):
        duration = self.duration()
        return "%dd %02d:%02d" % (duration.days, duration.seconds // 3600, (duration.seconds // 60) % 60)

    def amount_saved(self):
        duration = self.duration()
        duration_in_sec = duration.days * 86400 + duration.seconds
        return (duration_in_sec * self.pack_price * self.cigarettes_per_day) / (self.pack_size * 86400)

    def amount_donated(self):
        from donation.models import Payment
        return Payment.objects.filter(quitter=self.user)\
            .aggregate(sum=Sum('amount'))['sum'] or 0

    def amount_pledged(self):
        return self.amount_saved() * self.donation_percentage / 100

    def amount_to_donate(self):
        return self.amount_pledged() - self.amount_donated()

    def supporter_donations(self):
        from supporter.models import Pledge
        return Pledge.objects.amount_donated(self.user)

    def supporter_pledges(self):
        from supporter.models import Pledge
        return Pledge.objects.amount_pledged(self.user)

    def supporter_donations_and_pledges(self):
        return self.supporter_donations() + self.supporter_pledges()

    def total_amount(self):
        return self.amount_donated()\
            + self.amount_pledged()\
            + self.supporter_donations()\
            + self.supporter_pledges()

    def set_hash(self, hash):
        self.hash = hashlib.sha1(str(hash)).hexdigest()


class Beneficiary(models.Model):
    quitter = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    url = models.URLField()
    donate_url = models.URLField()
    banner = models.ImageField(upload_to='b/banner', null=True, blank=True)
    banner_font_theme = models.CharField(max_length=10,
                                         choices=(('', _('dark')), ('light', _('light'))),
                                         blank=True,
                                         default='')
    banner_copyright = models.CharField(max_length=255, blank=True, default='')
    logo = models.ImageField(upload_to='b/logo', null=True, blank=True)

    def __unicode__(self):
        return u"%s" % (self.name)

    def clone(self, user):
        return self.__class__.objects.create(quitter=user,
                                             name=self.name,
                                             url=self.url,
                                             donate_url=self.donate_url)
