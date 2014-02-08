from django.db import models
from django.contrib.auth.models import User
from quitter.models import Beneficiary
import datetime
from django.db.models.aggregates import Sum


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
    days = models.PositiveIntegerField()
    amount = models.PositiveIntegerField()
    confirmed = models.BooleanField(default=False)
    honored = models.BooleanField(default=False)
    hash = models.CharField(max_length=128, unique=True)

    objects = PledgeManager()

    def __unicode__(self):
        return "%s -> %s: $%s after %s days" % (self.supporter,
                                                self.beneficiary,
                                                self.amount,
                                                self.days)

    def reached(self):
        return (datetime.datetime.utcnow() - self.quitter.profile.quit_date).days >= self.days
