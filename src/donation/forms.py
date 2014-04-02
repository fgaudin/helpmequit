from django import forms
from donation.models import Payment


class DonateForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount']
