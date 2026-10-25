from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.trading.models import LeadTrader, TradingPair, SystemSettings

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with sample data for demo'

    def handle(self, *args, **kwargs):
        # ۱. تنظیمات سیستم
        SystemSettings.objects.get_or_create(pk=1)

        # ۲. جفت‌ارزها
        pairs = [
            ('BTC/USDT', 'Alpha Strategy'),
            ('ETH/USDT', 'Momentum Pro'),
            ('SOL/USDT', 'Solar Grid'),
            ('BNB/USDT', 'Binance Flow'),
        ]
        for symbol, name in pairs:
            TradingPair.objects.get_or_create(
                symbol=symbol,
                defaults={
                    'display_name': name,
                    'real_price': 100,
                    'manipulation_percent': 0,
                    'daily_growth_percent': 1.5,
                    'is_active': True,
                }
            )

        # ۳. تریدرهای نمونه
        traders = [
            {
                'name': 'Alex Chen',
                'roi_30d': 45.5,
                'pnl_30d': 12500,
                'aum': 250000,
                'win_rate': 88,
                'risk_level': 2,
                'followers_count_manual': 340,
                'capacity': 500,
                'chart_history_json': [0, 5, 12, 18, 25, 33, 40, 45.5],
                'target_profit_growth': 1.2,
            },
            {
                'name': 'Sarah Kim',
                'roi_30d': 72.3,
                'pnl_30d': 34000,
                'aum': 580000,
                'win_rate': 92,
                'risk_level': 3,
                'followers_count_manual': 720,
                'capacity': 1000,
                'chart_history_json': [0, 8, 20, 35, 48, 60, 68, 72.3],
                'target_profit_growth': 2.0,
            },
            {
                'name': 'Mike Ross',
                'roi_30d': 28.7,
                'pnl_30d': 8200,
                'aum': 120000,
                'win_rate': 78,
                'risk_level': 1,
                'followers_count_manual': 150,
                'capacity': 300,
                'chart_history_json': [0, 3, 8, 14, 19, 24, 27, 28.7],
                'target_profit_growth': 0.8,
            },
        ]
        for t in traders:
            LeadTrader.objects.get_or_create(name=t['name'], defaults=t)

        # ۴. یک کاربر دمو (برای اینکه بشود لاگین کرد و صفحه را دید)
        if not User.objects.filter(email='demo@smarttrade.com').exists():
            User.objects.create_user(
                username='demo@smarttrade.com',
                email='demo@smarttrade.com',
                password='demo12345',
                balance=1000,
                is_verified=True,
            )

        self.stdout.write(self.style.SUCCESS('Sample data seeded successfully.'))