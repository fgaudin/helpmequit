from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models.aggregates import Sum


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
        return self.amount_saved() * self.donation_percentage / 100 - self.amount_donated()

    def supporter_donations(self):
        from supporter.models import Pledge
        return Pledge.objects.amount_donated(self.user)

    def supporter_pledges(self):
        from supporter.models import Pledge
        return Pledge.objects.amount_pledged(self.user)

    def total_amount(self):
        return self.amount_donated()\
            + self.amount_pledged()\
            + self.supporter_donations()\
            + self.supporter_pledges()


class Beneficiary(models.Model):
    quitter = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    donate_url = models.URLField()

    def __unicode__(self):
        return self.name

    def amount_received(self):
        pass
