from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    list_display = ('user', 'tx_type', 'amount', 'currency', 'status', 'status_colored', 'created_at')
    list_filter = ('status', 'tx_type', 'created_at')
    search_fields = ('user__username', 'tx_hash')
    
    list_editable = ('status',)
    
    actions = ['approve_transactions', 'reject_transactions']

    def status_colored(self, obj):
        colors = {
            'pending': '#f39c12',  
            'approved': '#2ecc71', 
            'rejected': '#e74c3c', 
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display().upper()
        )
    status_colored.short_description = 'Visual Status'

    @admin.action(description='Approve selected transactions')
    def approve_transactions(self, request, queryset):
        count = 0
        for tx in queryset:
            if tx.status == 'pending':
                tx.status = 'approved'
                tx.save() 
                count += 1
        self.message_user(request, f"Successfully approved {count} transactions.")

    @admin.action(description='Reject selected transactions')
    def reject_transactions(self, request, queryset):
        count = 0
        for tx in queryset:
            if tx.status == 'pending':
                tx.status = 'rejected'
                tx.save() 
                count += 1
        self.message_user(request, f"Successfully rejected {count} transactions.")