from django.db import models
from quitter.models import Beneficiary
from django.contrib.auth.models import User


class Payment(models.Model):
    quitter = models.ForeignKey(User)
    beneficiary = models.ForeignKey(Beneficiary)
    amount = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
