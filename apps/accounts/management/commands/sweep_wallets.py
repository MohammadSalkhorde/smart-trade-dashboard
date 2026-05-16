from django.core.management.base import BaseCommand
from apps.accounts.tron_service import TronWalletService

class Command(BaseCommand):
    help = 'Sweep USDT from all user wallets to master wallet'

    def handle(self, *args, **options):
        service = TronWalletService()
        
        if not service.api_key:
            self.stdout.write(self.style.ERROR('TRONGRID_API_KEY not set in settings.py'))
            return
        
        if not service.master_address:
            self.stdout.write(self.style.ERROR('MASTER_WALLET_ADDRESS not set in settings.py'))
            return
        
        self.stdout.write('Checking user wallets...')
        results = service.sweep_all_wallets()
        
        self.stdout.write(self.style.SUCCESS(f'Swept {len(results)} wallets'))
        for result in results:
            self.stdout.write(f"  {result['user']}: ${result['amount']} - TX: {result['tx_id']}")