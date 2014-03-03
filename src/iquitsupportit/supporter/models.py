from django.db import models
from django.contrib.auth.models import User
from quitter.models import Beneficiary
import datetime
from django.db.models.aggregates import Sum
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _


class PledgeManager(models.Manager):
    def amount_pledged(self, quitter):
        return self.filter(honored=False,
                           confirmed=True,
                           beneficiary__quitter=quitter)\
            .aggregate(sum=Sum('amount'))['sum'] or 0

    def amount_donated(self, quitter):
        return self.filter(honored=True, beneficiary__quitter=quitter)\
            .aggregate(sum=Sum('amount'))['sum'] or 0


class Pledge(models.Model):
    supporter = models.ForeignKey(User, related_name='pledges')
    beneficiary = models.ForeignKey(Beneficiary, related_name='pledges_received')
    days = models.PositiveIntegerField(verbose_name=_('Days'))
    amount = models.PositiveIntegerField(verbose_name=_('Amount'))
    confirmed = models.BooleanField(default=False)
    honored = models.BooleanField(default=False)
    hash = models.CharField(max_length=128, unique=True)
    remind_attempts = models.PositiveIntegerField(default=0)
    last_attempt = models.DateTimeField(null=True, blank=True)

    objects = PledgeManager()

    def __unicode__(self):
        status = 'unconfirmed'
        if self.honored:
            status = 'honored'
        elif self.confirmed:
            status = 'confirmed'

        return "%s -> %s: $%s after %s days [%s]" % (self.supporter.email,
                                                     self.beneficiary,
                                                     self.amount,
                                                     self.days,
                                                     status)

    def should_send(self):
        if not self.last_attempt:
            return True
        else:
            next_attempt = self.last_attempt + datetime.timedelta(self.remind_attempts ** 2)
            if now() >= next_attempt:
                return True

        return False
