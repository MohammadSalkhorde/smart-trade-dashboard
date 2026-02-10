from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",) 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'password1' in self.fields:
            self.fields['password1'].label = "Password"
        if 'password2' in self.fields:
            self.fields['password2'].label = "Confirm Password"
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control border-0 bg-light py-2 px-3',
                'style': 'border-radius: 10px;',
                'placeholder': f'Enter your {field.label.lower()}'
            })

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValidationError("Please enter a valid professional email address.")

        valid_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'icloud.com', 'protonmail.com']
        domain = email.split('@')[-1]
        if domain not in valid_domains:
            raise ValidationError(f"For security, please use a major provider like Gmail or Yahoo.")

        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")

        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 4:
            raise ValidationError("Username must be at least 4 characters long.")
        return username

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'wallet_address']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
            })
        self.fields['email'].widget.attrs['readonly'] = True