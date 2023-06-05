from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
import re

class MyForm(forms.Form):
    my_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}))

class MyCreateUserForm(UserCreationForm):
    phone = forms.IntegerField()
    user_id = forms.IntegerField(required=False)
    first_name = forms.CharField(max_length=30,required=True)
    last_name = forms.CharField(max_length=30,required=True)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('user_id','username','first_name', 'last_name', 'email', 'password1', 'password2','phone')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = True
        self.fields['user_id'].required = False
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if len(str(phone)) != 10:
            raise forms.ValidationError('Phone number must be 10 digits long.')
        return phone

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if re.search(r'[\d\W]', first_name):
            raise forms.ValidationError("First name should only contain letters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if re.search(r'[\d\W]', last_name):
            raise forms.ValidationError("Last name should only contain letters.")
        return last_name


class MyPasswordResetForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'