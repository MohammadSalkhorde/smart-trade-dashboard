import secrets
import requests
from django.conf import settings
from decimal import Decimal

class TronWalletService:

    def __init__(self):
        self.api_url = getattr(settings, 'TRONGRID_API_URL', 'https://api.trongrid.io')
        self.api_key = getattr(settings, 'TRONGRID_API_KEY', '')
        self.master_address = getattr(settings, 'MASTER_WALLET_ADDRESS', '')

    def _get_headers(self):
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['TRON-PRO-API-KEY'] = self.api_key
        return headers

    def generate_wallet(self):
        private_key_bytes = secrets.token_bytes(32)
        private_key_hex = private_key_bytes.hex()
        prefix = "T"
        random_part = secrets.token_hex(16).upper()[:33]
        address = prefix + random_part
        return {'address': address, 'private_key': private_key_hex}

    def get_or_create_user_wallet(self, user):
        from .models import UserWallet
        wallet, created = UserWallet.objects.get_or_create(
            user=user,
            defaults={
                'address': self.generate_wallet()['address'],
                'private_key': self.generate_wallet()['private_key']
            }
        )
        return wallet, created

    def get_usdt_balance(self, address):
        try:
            url = f"{self.api_url}/v1/accounts/{address}"
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                data = response.json()
                trc20_tokens = data.get('data', [{}])[0].get('trc20', [])
                for token in trc20_tokens:
                    if 'USDT' in token:
                        raw_amount = token.get('USDT', '0')
                        return float(raw_amount) / 1_000_000
            return 0.0
        except Exception:
            return 0.0

    def check_all_user_wallets_and_sweep(self):
        from .models import UserWallet
        from apps.transactions.models import Transaction
        from django.contrib.auth import get_user_model
        from django.utils import timezone

        User = get_user_model()
        wallets = UserWallet.objects.filter(is_active=True)
        results = []

        for wallet in wallets:
            balance = self.get_usdt_balance(wallet.address)
            min_balance = getattr(settings, 'MIN_BALANCE_TO_SWEEP', 5)

            if balance >= min_balance:
                Transaction.objects.get_or_create(
                    user=wallet.user,
                    tx_type='deposit',
                    amount=Decimal(str(balance)),
                    status='approved',
                    network='TRC20',
                    defaults={'tx_hash': f"AUTO_{wallet.address}_{timezone.now().timestamp()}"}
                )
                wallet.user.balance += Decimal(str(balance))
                wallet.user.save()
                wallet.last_checked_at = timezone.now()
                wallet.save()
                results.append({'user': wallet.user.email, 'amount': balance, 'status': 'swept'})

        return results