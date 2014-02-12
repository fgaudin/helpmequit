from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import SetPasswordForm as DjangoSetPasswordForm
from quitter.models import Profile, Beneficiary
from django.contrib.auth.models import User


class SignupForm(forms.Form):
    email = forms.EmailField(label=_('Email'))

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['placeholder'] = self.fields[field].label
            self.fields[field].widget.attrs['required'] = True


class LoginForm(forms.Form):
    email = forms.EmailField(label=_('Email'))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['placeholder'] = self.fields[field].label
            self.fields[field].widget.attrs['required'] = True


class SetPasswordForm(DjangoSetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super(SetPasswordForm, self).__init__(user, *args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['placeholder'] = self.fields[field].label
            self.fields[field].widget.attrs['required'] = True


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user', 'hash']


class BeneficiaryForm(forms.ModelForm):
    class Meta:
        model = Beneficiary
        exclude = ['quitter']
