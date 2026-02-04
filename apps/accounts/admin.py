from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # فیلدهایی که در لیست اصلی کاربران نمایش داده می‌شود
    list_display = ('email', 'username', 'balance', 'referral_code', 'is_verified', 'is_staff')
    list_filter = ('is_verified', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username', 'referral_code')
    ordering = ('email',)

    # فیلدبندی بخش ویرایش کاربر
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Exchange Assets', {'fields': ('balance', 'wallet_address', 'is_verified')}),
        ('Referral System', {'fields': ('referred_by', 'referral_code')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # فیلدهای فرم ساخت کاربر جدید (مثلاً در پنل ادمین)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Exchange Info', {'fields': ('email', 'balance', 'wallet_address', 'is_verified')}),
    )