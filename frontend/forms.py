import json
import urllib.request
from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from data.models import Group, Teacher
from .models import UnregisteredVKUserTimetablePermissions

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
        instance = super().save(commit=False)
        if self.cleaned_data.get('new_password'):
            instance.set_password(self.cleaned_data['new_password'])
        if commit:
            instance.save()
        return instance

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'new_password', 'new_password_confirm', 'email', 'old_password']

class AddVKUserPermissions(forms.Form):
    identifier = forms.CharField(label='ID, link or username', max_length=100)
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=False)
    teachers = forms.ModelMultipleChoiceField(queryset=Teacher.objects.all(), required=False)

    def clean_identifier(self):
        identifier_str = self.cleaned_data['identifier']

        if (identifier_str.find('/') != -1):
            identifier_str = identifier_str.split('/')[-1]

        api_data = json.loads(urllib.request.urlopen('https://api.vk.com/method/users.get?user_ids={0}&v=5.40'.format(identifier_str)).read().decode('cp1251'))
        if ('response' not in api_data) or (len(api_data['response']) == 0):
            raise ValidationError(_('No such user registered in VK'))

        return str(api_data['response'][0]['id'])

    class Meta:
        fields = ['identifier', 'groups', 'teachers']
