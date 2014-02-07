from django import forms
from supporter.models import Pledge


class PledgeForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Pledge
        fields = ['amount', 'days']
