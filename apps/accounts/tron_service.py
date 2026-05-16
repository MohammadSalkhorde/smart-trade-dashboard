import requests
from decimal import Decimal
from django.conf import settings
from django.utils import timezone

class TronWalletService:

    def __init__(self):
        self.api_url = getattr(settings, 'TRONGRID_API_URL', 'https://api.trongrid.io')
        self.api_key = getattr(settings, 'TRONGRID_API_KEY', '')
        self.master_address = getattr(settings, 'MASTER_WALLET_ADDRESS', '')
        self.usdt_contract = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

    def _get_headers(self):
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['TRON-PRO-API-KEY'] = self.api_key
        return headers

    def generate_wallet(self):
        if not self.api_key:
            raise Exception("TRONGRID_API_KEY is required. Please add it to settings.py")
        
        try:
            from tronpy import Tron
            from tronpy.providers import HTTPProvider
            
            provider = HTTPProvider(api_key=self.api_key, base_url=self.api_url)
            client = Tron(provider=provider)
            wallet = client.generate_address()
            
            return {
                'address': wallet['base58check_address'],
                'private_key': wallet['private_key']
            }
        except ImportError:
            import secrets
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
            defaults=self.generate_wallet()
        )
        return wallet, created

    def get_usdt_balance(self, address):
        try:
            url = f"{self.api_url}/v1/accounts/{address}"
            response = requests.get(url, headers=self._get_headers(), timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                trc20_tokens = data.get('data', [{}])[0].get('trc20', [])
                for token in trc20_tokens:
                    if 'USDT' in token:
                        raw_amount = token.get('USDT', '0')
                        return float(raw_amount) / 1_000_000
            return 0.0
        except Exception as e:
            print(f"Balance check error for {address}: {e}")
            return 0.0

    def transfer_usdt(self, from_address, from_private_key, to_address, amount):
        try:
            from tronpy import Tron
            from tronpy.providers import HTTPProvider
            from tronpy.keys import PrivateKey
            
            if not self.api_key:
                raise Exception("TRONGRID_API_KEY is required for transfer")
            
            provider = HTTPProvider(api_key=self.api_key, base_url=self.api_url)
            client = Tron(provider=provider)
            
            private_key = PrivateKey.fromhex(from_private_key)
            account = private_key.to_base58check_address()
            
            contract = client.get_contract(self.usdt_contract)
            amount_in_smallest = int(amount * 1_000_000)
            
            txn = (
                contract.functions.transfer(to_address, amount_in_smallest)
                .with_owner(account)
                .build()
                .sign(private_key)
            )
            
            result = txn.broadcast()
            
            return {
                'success': True,
                'tx_id': result['txid'],
                'amount': amount
            }
            
        except Exception as e:
            print(f"Transfer error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def sweep_user_wallet(self, wallet):
        min_balance = getattr(settings, 'MIN_BALANCE_TO_SWEEP', 5)
        balance = self.get_usdt_balance(wallet.address)
        
        if balance < min_balance:
            return None
        
        if not self.master_address:
            print("MASTER_WALLET_ADDRESS not set")
            return None
        
        if not self.api_key:
            print("TRONGRID_API_KEY not set - sweep skipped")
            return None
        
        transfer_result = self.transfer_usdt(
            wallet.address,
            wallet.private_key,
            self.master_address,
            balance
        )
        
        if transfer_result['success']:
            from apps.transactions.models import Transaction
            from django.contrib.auth import get_user_model
            
            Transaction.objects.create(
                user=wallet.user,
                tx_type='deposit',
                amount=Decimal(str(balance)),
                status='approved',
                tx_hash=transfer_result['tx_id'],
                network='TRC20'
            )
            
            wallet.user.balance += Decimal(str(balance))
            wallet.user.save()
            wallet.last_checked_at = timezone.now()
            wallet.save()
            
            return {
                'user': wallet.user.email,
                'amount': balance,
                'tx_id': transfer_result['tx_id']
            }
        
        return None

    def sweep_all_wallets(self):
        from .models import UserWallet
        
        wallets = UserWallet.objects.filter(is_active=True)
        results = []
        
        for wallet in wallets:
            result = self.sweep_user_wallet(wallet)
            if result:
                results.append(result)
        
        return results