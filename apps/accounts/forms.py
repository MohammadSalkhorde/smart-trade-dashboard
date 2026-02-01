from django import forms  # این خط اصلاح شد
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # استایل‌دهی به فیلدها برای اینکه با ظاهر شیک ما همخوانی داشته باشند
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control border-0 bg-light py-2 px-3',
                'style': 'border-radius: 10px;',
                'placeholder': f'Enter {field.capitalize()}'
            })
            
from .models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'wallet_address']
        widgets = {
            field: forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'})
            for field in ['first_name', 'last_name', 'email', 'wallet_address']
        }