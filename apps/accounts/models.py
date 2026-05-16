from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Email Address")
    
    balance = models.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Total Balance (USDT)"
    )
    
    wallet_address = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="User Wallet Address"
    )

    is_verified = models.BooleanField(default=True)
    
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    referral_code = models.CharField(max_length=10, unique=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
            
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    @property
    def total_withdrawals(self):
        return self.transaction_set.filter(tx_type='withdraw', status='approved').aggregate(
            models.Sum('amount'))['amount__sum'] or 0

    @property
    def total_deposits(self):
        return self.transaction_set.filter(tx_type='deposit', status='approved').aggregate(
            models.Sum('amount'))['amount__sum'] or 0
    
    @property
    def referral_earnings(self):
        """
        نمایش ۱۰ درصد از تمام واریزی‌های تایید شده زیرمجموعه‌ها در داشبورد
        """
        from apps.transactions.models import Transaction
        my_referrals = User.objects.filter(referred_by=self)
        
        total_deposited = Transaction.objects.filter(
            user__in=my_referrals,
            tx_type='deposit',
            status='approved'
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0
        
        return round(float(total_deposited) * 0.10, 2)

class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE) 
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email}"
    


class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('Technical Support', 'Technical Support'),
        ('Investment Inquiry', 'Investment Inquiry'),
        ('Account Issues', 'Account Issues'),
        ('Feedback', 'Feedback'),
    ]

    full_name = models.CharField(max_length=255, verbose_name="نام کامل")
    email = models.EmailField(verbose_name="ایمیل")
    subject = models.CharField(max_length=100, choices=SUBJECT_CHOICES, verbose_name="موضوع")
    message = models.TextField(verbose_name="متن پیام")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده؟")

    class Meta:
        verbose_name = "contact us message"
        verbose_name_plural = "contact us messages"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.subject}"
    
    
from django.conf import settings


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('pending', 'Pending'),
        ('closed', 'Closed'),
    ]
    
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Ticket {self.id} - {self.subject} ({self.user.email})"

class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    is_admin_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # پیام‌ها به ترتیب زمان ارسال

    def __str__(self):
        return f"Message by {self.sender.email} on Ticket #{self.ticket.id}"
    
    
class UserWallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tron_wallet')
    address = models.CharField(max_length=255, unique=True)
    private_key = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_checked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "User TRON Wallet"
        verbose_name_plural = "User TRON Wallets"

    def __str__(self):
        return f"{self.user.email} - {self.address[:10]}..."