from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils.timezone import now


class Profile(models.Model):
    user = models.OneToOneField(User)
    slug = models.CharField(max_length=255, unique=True)
    quit_date = models.DateTimeField()
    cigarettes_per_day = models.PositiveIntegerField()
    pack_price = models.DecimalField(max_digits=5, decimal_places=2)
    pack_size = models.PositiveIntegerField()
    donation_percentage = models.PositiveIntegerField(default=100)
    current_beneficiary = models.ForeignKey('Beneficiary')

    def __unicode__(self):
        return self.user.__unicode__()

    def duration(self):
        return now() - self.quit_date

    def duration_str(self):
        duration = self.duration()
        return "%dd %02d:%02d" % (duration.days, duration.seconds // 3600, (duration.seconds // 60) % 60)

    def amount_saved(self):
        duration = self.duration()
        duration_in_sec = duration.days * 86400 + duration.seconds
        return (duration_in_sec * self.pack_price * self.cigarettes_per_day) / (self.pack_size * 86400)

    def amount_donated(self):
        return self.amount_saved() * self.donation_percentage / 100


class Beneficiary(models.Model):
    quitter = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    donate_url = models.URLField()

    def __unicode__(self):
        return self.name
