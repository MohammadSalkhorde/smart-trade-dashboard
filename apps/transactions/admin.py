from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'tx_type', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'tx_type', 'created_at')
    search_fields = ('user__username', 'tx_hash')
    
    # این خط باعث می‌شود در لیست اصلی بتوان وضعیت را سریع تغییر داد و ذخیره کرد
    list_editable = ('status',)
    
    # رنگی کردن وضعیت‌ها برای تشخیص سریع‌تر
    def get_status_display(self, obj):
        from django.utils.html import format_html
        colors = {
            'pending': '#f39c12',  # نارنجی
            'approved': '#2ecc71', # سبز
            'rejected': '#e74c3c', # قرمز
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.status.upper()
        )