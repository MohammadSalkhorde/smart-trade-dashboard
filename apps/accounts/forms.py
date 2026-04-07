from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()

class RegisterForm(forms.ModelForm):
    # تعریف دستی فیلدها برای کنترل کامل
    email = forms.EmailField(label="Email Address")
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # اضافه کردن کلاس‌های CSS به همه فیلدها
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control border-0 bg-light py-2 px-3',
                'style': 'border-radius: 10px;',
                'placeholder': f'Enter your {field.label.lower()}'
            })

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        # اینجا همون جاییه که گفتی روی ۴ کاراکتر گیر بده
        if password and len(password) < 4:
            raise ValidationError("Password must be at least 4 characters long.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        # چک کردن مطابقت دو پسورد
        if p1 and p2 and p1 != p2:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # ست کردن پسورد به صورت هش شده (امنیت)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

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