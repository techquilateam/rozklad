from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class EditUserProfile(forms.ModelForm):
    username = forms.CharField(required=True, min_length=5, max_length=30)
    new_password = forms.CharField(required=False, min_length=8, max_length=32, widget=forms.PasswordInput)
    new_password_confirm = forms.CharField(required=False, widget=forms.PasswordInput)
    old_password = forms.CharField(required=True, widget=forms.PasswordInput)

    def clean_new_password_confirm(self):
        if self.cleaned_data.get('new_password') or self.cleaned_data.get('new_password_confirm'):
            if not (self.cleaned_data.get('new_password') and self.cleaned_data.get('new_password_confirm')):
                raise ValidationError(_('Passwords don\'t match'))
            if self.cleaned_data['new_password'] != self.cleaned_data['new_password_confirm']:
                raise ValidationError(_('Passwords don\'t match'))

    def clean_old_password(self):
        if not self.instance.check_password(self.cleaned_data['old_password']):
            raise ValidationError(_('Wrong password'))

    def save(self, commit=True):
        instance = super(EditUserProfile, self).save(commit=False)
        if self.cleaned_data.get('new_password'):
            instance.set_password(self.cleaned_data['new_password'])
        if commit:
            instance.save()
        return instance

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'new_password', 'new_password_confirm', 'email', 'old_password']
