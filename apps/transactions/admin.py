from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    # اضافه کردن ستون‌های شبکه و مشخصات پیگیری برای مدیریت راحت‌تر دستی
    list_display = ('user', 'tx_type', 'network', 'amount', 'get_target_details', 'status', 'status_colored', 'created_at')
    list_filter = ('status', 'tx_type', 'network', 'created_at')
    search_fields = ('user__username', 'tx_hash')
    
    # امکان ویرایش سریع وضعیت مستقیم از داخل لیست
    list_editable = ('status',)
    
    actions = ['approve_transactions', 'reject_transactions']

    @admin.display(description="Wallet / TXID")
    def get_target_details(self, obj):
        """تفکیک نمایش مأموریت فیلد هش براساس نوع تراکنش در پنل ادمین"""
        if not obj.tx_hash:
            return format_html('<span style="color: #999;">N/A</span>')
        
        if obj.tx_type == 'deposit':
            return format_html('<span style="font-family: monospace;" title="User Transaction Hash">TXID: {}</span>', obj.tx_hash[:16] + "...")
        else:
            return format_html('<span style="font-family: monospace; color: #0052ff;" title="User Destination Wallet">Wallet: {}</span>', obj.tx_hash)

    @admin.display(description="Visual Status")
    def status_colored(self, obj):
        colors = {
            'pending': '#f39c12',   # نارنجی
            'approved': '#2ecc71',  # سبز
            'rejected': '#e74c3c',  # قرمز
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display().upper()
        )

    @admin.action(description='Approve selected transactions (Updates Balance)')
    def approve_transactions(self, request, queryset):
        count = 0
        # استفاده از تک‌تک آرا برای فعال شدن متد save داخلی مدل جهت اعمال موجودی
        for tx in queryset:
            if tx.status == 'pending':
                tx.status = 'approved'
                tx.save()  # این خط متد save مدل را صدا می‌زند و کیف پول کاربر دستی شارژ می‌شود
                count += 1
        self.message_user(request, f"Successfully approved {count} transactions and updated user balances.")

    @admin.action(description='Reject selected transactions (Reverts Balance if Withdraw)')
    def reject_transactions(self, request, queryset):
        count = 0
        for tx in queryset:
            if tx.status == 'pending':
                tx.status = 'rejected'
                tx.save()  # این خط در صورت برداشت، پول کسر شده را به کاربر پس می‌دهد
                count += 1
        self.message_user(request, f"Successfully rejected {count} transactions.")