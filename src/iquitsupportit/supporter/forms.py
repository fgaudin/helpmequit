from django import forms
from supporter.models import Pledge
from django.utils.translation import gettext_lazy as _


class PledgeForm(forms.ModelForm):
    email = forms.EmailField(label=_('Your email'))

    class Meta:
        model = Pledge
        fields = ['amount', 'days']

    def __init__(self, *args, **kwargs):
        super(PledgeForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['placeholder'] = self.fields[field].label
            # self.fields[field].widget.attrs['required'] = True
