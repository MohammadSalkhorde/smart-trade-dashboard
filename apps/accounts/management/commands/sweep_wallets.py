from django.core.management.base import BaseCommand
from apps.accounts.tron_service import TronWalletService

class Command(BaseCommand):
    help = 'Sweep USDT from all user wallets to master wallet'

    def handle(self, *args, **options):
        service = TronWalletService()
        results = service.check_all_user_wallets_and_sweep()
        self.stdout.write(f"Swept {len(results)} wallets")
        for result in results:
            self.stdout.write(f"  {result['user']}: ${result['amount']}")