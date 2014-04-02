from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models.aggregates import Sum
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import os
import uuid
import random
import string
from django.core import validators
import re
from django.core.urlresolvers import reverse


class ProfileManager(models.Manager):
    def create_profile(self, user):
        default_profile = Profile.objects.get(slug=settings.DEFAULT_PROFILE)
        default_beneficiary = default_profile.current_beneficiary
        beneficiary = default_beneficiary.clone(user)

        base_slug = user.first_name.lower() or ''.join(random.choice(string.lowercase) for i in range(8))
        slug = base_slug
        i = 1
        while self.filter(slug=slug).exists():
            slug = u'%s%d' % (base_slug, i)
            i += 1

        return self.create(user=user,
                           slug=slug,
                           quit_date=now(),
                           cigarettes_per_day=10,
                           pack_price=7,
                           pack_size=20,
                           donation_percentage=100,
                           current_beneficiary=beneficiary,
                           testimony='Write your testimony here!',
                           video_embed_url=default_profile.video_embed_url,
                           picture=default_profile.picture)


def get_profile_upload_path(instance, filename):
    return os.path.join('%d' % instance.user.id,
                        'pic',
                        '%s_%s' % (uuid.uuid4(), filename))


class Profile(models.Model):
    user = models.OneToOneField(User)
    slug = models.CharField(max_length=255, unique=True,
        validators=[
            validators.RegexValidator(re.compile('^[\w.]+$'), _('Only letters, numbers and . are accepted.'), 'invalid')
        ])
    quit_date = models.DateTimeField(verbose_name=_('Quit date'))
    cigarettes_per_day = models.PositiveIntegerField(verbose_name=_('Cigarettes per day'))
    pack_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Pack price'))
    pack_size = models.PositiveIntegerField(verbose_name=_('Pack size'))
    donation_percentage = models.PositiveIntegerField(default=100, verbose_name=_('Donation percentage'))
    currency = models.CharField(max_length=10, default='$', verbose_name=_('Currency'))
    current_beneficiary = models.ForeignKey('Beneficiary', verbose_name=_('Beneficiary'))
    testimony = models.TextField(verbose_name=_('Testimony'))
    video_embed_url = models.URLField(null=True, blank=True, verbose_name=_('Video embed url'))
    picture = models.ImageField(upload_to=get_profile_upload_path, null=True, blank=True, verbose_name=_('Picture'))
    language = models.CharField(max_length=8,
                                choices=settings.LANGUAGES,
                                verbose_name=_('Language'),
                                default='en')

    objects = ProfileManager()

    def __unicode__(self):
        return u'%s' % self.user.email

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
        return self.amount_pledged()\
            + self.supporter_donations()\
            + self.supporter_pledges()

    def link(self):
        return '<a href="%s">%s</a>' % (reverse('user', args=[self.slug]),
                                        self.user.first_name)


def get_banner_upload_path(instance, filename):
    return os.path.join('u',
                        '%d' % instance.quitter.id,
                        'banner',
                        '%s_%s' % (uuid.uuid4(), filename))


def get_logo_upload_path(instance, filename):
    return os.path.join('u',
                        '%d' % instance.quitter.id,
                        'logo',
                        '%s_%s' % (uuid.uuid4(), filename))


class Beneficiary(models.Model):
    quitter = models.ForeignKey(User)
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    url = models.URLField(verbose_name=_('Url'))
    donate_url = models.URLField(verbose_name=_('Donate url'))
    banner = models.ImageField(upload_to=get_banner_upload_path,
                               null=True,
                               blank=True,
                               verbose_name=_('Banner'))
    banner_font_theme = models.CharField(max_length=10,
                                         choices=(('', _('dark')), ('light', _('light'))),
                                         blank=True,
                                         default='',
                                         verbose_name=_('Font color'))
    banner_copyright = models.CharField(max_length=255,
                                        blank=True,
                                        default='',
                                        verbose_name=_('Banner copyright'))
    logo = models.ImageField(upload_to=get_logo_upload_path,
                             null=True,
                             blank=True,
                             verbose_name=_('Logo'))

    def __unicode__(self):
        return u"%s" % (self.name)

    def clone(self, user):
        return self.__class__.objects.create(quitter=user,
                                             name=self.name,
                                             url=self.url,
                                             donate_url=self.donate_url,
                                             banner=self.banner,
                                             banner_font_theme=self.banner_font_theme,
                                             banner_copyright=self.banner_copyright,
                                             logo=self.logo)

    def link(self):
        return '<a href="%s" target="_blank">%s</a>' % (self.url,
                                                        self.name)
