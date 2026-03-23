from django.contrib import admin
from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.admin import helpers
from .models import SystemSettings, TradingPair, LeadTrader, FollowedTrader

# --- Form for Injection Action ---
class ActionValueForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    value = forms.FloatField(
        label="Profit Percentage (%)", 
        help_text="Enter the amount to add to the current ROI (e.g., 5.2 or -2.1)",
        widget=forms.NumberInput(attrs={'step': '0.01', 'style': 'width: 100%;'})
    )

# --- LeadTrader Admin ---
@admin.register(LeadTrader)
class LeadTraderAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_manual_mode', 'roi_30d', 'win_rate', 'max_drawdown', 'total_copiers', 'risk_level')
    list_editable = ('is_manual_mode', 'risk_level', 'win_rate', 'max_drawdown') 
    actions = ['inject_custom_profit', 'apply_target_growth_step']
    readonly_fields = ('roi_30d', 'chart_history_json')

    fieldsets = (
        ('Identity & Mode', {
            'fields': ('name', 'avatar', 'is_manual_mode', 'risk_level', 'capacity')
        }),
        ('Algorithm & Performance', {
            'fields': ('roi_30d', 'win_rate', 'max_drawdown', 'chart_history_json', 'target_profit_growth'),
        }),
    )

    def inject_custom_profit(self, request, queryset):
        action_checkbox_name = helpers.ACTION_CHECKBOX_NAME
        if 'apply' in request.POST:
            form = ActionValueForm(request.POST)
            if form.is_valid():
                value = form.cleaned_data['value']
                for trader in queryset:
                    trader.add_profit_point(value)
                self.message_user(request, f"Successfully injected {value}% profit to {queryset.count()} traders.")
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = ActionValueForm(initial={
                '_selected_action': request.POST.getlist(action_checkbox_name)
            })
        
        return render(request, 'admin/action_value_form.html', {
            'items': queryset, 
            'form': form, 
            'title': 'Execute Profit Injection'
        })
    inject_custom_profit.short_description = "Inject Custom Profit (%)"

    @admin.action(description='Apply one step of Target Growth (1/7)')
    def apply_target_growth_step(self, request, queryset):
        for trader in queryset:
            if trader.target_profit_growth > 0:
                trader.add_profit_point(trader.target_profit_growth / 7)
        self.message_user(request, "Target growth steps applied successfully.")

# --- TradingPair Admin ---
@admin.register(TradingPair)
class TradingPairAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'symbol', 'real_price', 'manipulation_percent', 'display_price', 'is_active')
    list_editable = ('manipulation_percent', 'is_active')
    search_fields = ('symbol', 'display_name')
    list_filter = ('is_active',)

# --- SystemSettings Admin (اصلاح شده) ---
@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    # اضافه کردن هر دو آدرس به لیست نمایش
    list_display = ('site_name', 'tron_wallet_address', 'bsc_wallet_address', 'min_deposit_amount')
    
    # چیدمان فیلدها در صفحه ویرایش تنظیمات
    fieldsets = (
        ('General Settings', {
            'fields': ('site_name', 'min_deposit_amount')
        }),
        ('Crypto Wallets (Deposit)', {
            'fields': ('tron_wallet_address', 'bsc_wallet_address'),
            'description': 'Enter the wallet addresses where users should send their USDT.'
        }),
    )

    def has_add_permission(self, request):
        return not SystemSettings.objects.exists()

# --- FollowedTrader Admin ---
@admin.register(FollowedTrader)
class FollowedTraderAdmin(admin.ModelAdmin):
    list_display = ('user', 'trader', 'investment_amount', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'trader__name')