from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'balance', 'referral_code', 'is_verified', 'is_staff', 'is_banned')
    list_editable = ('is_banned',)
    list_filter = ('is_banned', 'is_verified', 'is_staff', 'is_superuser') # is_banned را به فیلترها هم اضافه کنید
    search_fields = ('email', 'username', 'referral_code')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Exchange Assets', {'fields': ('balance', 'wallet_address', 'is_verified')}),
        ('Referral System', {'fields': ('referred_by', 'referral_code')}),
        # در اینجا is_banned را اضافه کردیم:
        ('Permissions', {'fields': ('is_active', 'is_banned', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Exchange Info', {'fields': ('email', 'balance', 'wallet_address', 'is_verified', 'is_banned')}),
    )



from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    # نمایش ستون‌ها به شکلی جذاب‌تر
    list_display = ('full_name_styled', 'email', 'subject_badge', 'created_at_formatted', 'is_read')
    
    # فیلترهای هوشمند در سمت راست
    list_filter = ('is_read', 'subject', 'created_at')
    
    # جستجوی پیشرفته در محتوا
    search_fields = ('full_name', 'email', 'message', 'subject')
    
    # فیلد فقط خواندنی (برای امنیت داده‌ها)
    readonly_fields = ('full_name', 'email', 'subject', 'message', 'created_at')
    
    # قابلیت ویرایش سریع وضعیت خوانده شدن در لیست
    list_editable = ('is_read',)
    
    # تعداد پیام در هر صفحه
    list_per_page = 20
    
    # مرتب‌سازی پیش‌فرض (جدیدترین‌ها اول)
    ordering = ('-created_at',)

    # --- متدهای سفارشی برای استایل‌دهی ---

    @admin.display(description="Sender Name")
    def full_name_styled(self, obj):
        """نمایش نام با استایل متفاوت اگر پیام خوانده نشده باشد"""
        if not obj.is_read:
            return format_html('<strong style="color: #0052ff;">{} (New)</strong>', obj.full_name)
        return obj.full_name

    @admin.display(description="Subject")
    def subject_badge(self, obj):
        """نمایش موضوع به صورت نشان (Badge) رنگی"""
        colors = {
            'Technical Support': '#dc3545',   # قرمز
            'Investment Inquiry': '#198754', # سبز
            'Account Issues': '#fd7e14',     # نارنجی
            'Feedback': '#0dcaf0',           # آبی روشن
        }
        color = colors.get(obj.subject, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px;">{}</span>',
            color, obj.subject
        )

    @admin.display(description="Received Date")
    def created_at_formatted(self, obj):
        """نمایش تاریخ به فرمت خواناتر"""
        return obj.created_at.strftime("%Y-%m-%d | %H:%M")

    # --- اکشن‌های گروهی ---
    actions = ['mark_as_read', 'mark_as_unread']

    @admin.action(description="Mark selected messages as Read")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, "Selected messages were marked as read.")

    @admin.action(description="Mark selected messages as Unread")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, "Selected messages were marked as unread.")

    # سازمان‌دهی فیلدها در صفحه مشاهده جزئیات پیام
    fieldsets = (
        ('Sender Information', {
            'fields': (('full_name', 'email'),)
        }),
        ('Message Content', {
            'fields': ('subject', 'message')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',), # این بخش را جمع‌شونده می‌کند
        }),
    )
    
    
class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 1 # اجازه درج پاسخ مستقیم در صفحه تیکت
    readonly_fields = ('created_at',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'status', 'urgency', 'created_at')
    list_filter = ('status', 'urgency')
    inlines = [TicketMessageInline] # پاسخ‌ها زیر تیکت نمایش داده می‌شوند