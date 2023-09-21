from typing import Any, Dict
from django import forms
from account.models import CustomUser

class RegistrationForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput())
    confirm_password=forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model=CustomUser
        fields=['first_name','last_name','email','phone_number','password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm,self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'

    def clean(self):
        cleaned_data=super(RegistrationForm,self).clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')

        if password!=confirm_password:
            raise forms.ValidationError('Password entered does not match!')
        