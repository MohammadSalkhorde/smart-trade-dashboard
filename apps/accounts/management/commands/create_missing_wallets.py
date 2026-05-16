from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.tron_service import TronWalletService
from apps.accounts.models import UserWallet

User = get_user_model()

class Command(BaseCommand):
    help = 'Create missing wallets for all existing users'

    def handle(self, *args, **options):
        service = TronWalletService()
        
        if not service.api_key:
            self.stdout.write(self.style.ERROR('TRONGRID_API_KEY not set in settings.py'))
            return
        
        users = User.objects.all()
        total_users = users.count()
        created_count = 0
        already_exist_count = 0
        error_count = 0
        
        self.stdout.write(f'Checking {total_users} users...')
        
        for user in users:
            try:
                wallet, created = UserWallet.objects.get_or_create(
                    user=user,
                    defaults=service.generate_wallet()
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'  Created: {user.email} -> {wallet.address}')
                else:
                    already_exist_count += 1
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f'  Error for {user.email}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created: {created_count}, Already exist: {already_exist_count}, Errors: {error_count}'
        ))