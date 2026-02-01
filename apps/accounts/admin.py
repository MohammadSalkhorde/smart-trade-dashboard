from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # اضافه کردن فیلد Balance به لیست کاربران در ادمین
    list_display = ('username', 'email', 'balance', 'is_staff', 'is_verified')
    
    # اضافه کردن فیلد Balance به بخش ویرایش کاربر
    fieldsets = UserAdmin.fieldsets + (
        ('Exchange Info', {'fields': ('balance', 'wallet_address', 'is_verified')}),
    )
    
    # فیلدهای اضافه برای ساخت کاربر جدید
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Exchange Info', {'fields': ('balance', 'wallet_address', 'is_verified')}),
    )