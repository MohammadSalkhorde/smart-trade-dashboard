from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'tx_type', 'amount', 'status', 'created_at')
    list_filter = ('status', 'tx_type')
    search_fields = ('tx_hash', 'user__username')
    list_editable = ('status',) # اینجا ادمین فقط با یک کلیک وضعیت را به Approved تغییر می‌دهد