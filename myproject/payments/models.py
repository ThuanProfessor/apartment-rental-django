from django.db import models
from django.contrib.auth import get_user_model
from properties.models import Property
import uuid

User = get_user_model()

class PaymentMethod(models.Model):
    PAYMENT_TYPES = [
        ('vnpay', 'VNPay'),
        ('momo', 'MoMo'),
        ('bank_transfer', 'Chuyển khoản ngân hàng'),
        ('cash', 'Tiền mặt'),
    ]
    
    name = models.CharField(max_length=50, choices=PAYMENT_TYPES, unique=True)
    display_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    def __str__(self):
        return self.display_name

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Đặt cọc'),
        ('rent_payment', 'Thanh toán tiền thuê'),
        ('service_fee', 'Phí dịch vụ'),
        ('refund', 'Hoàn tiền'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Đang xử lý'),
        ('completed', 'Hoàn thành'),
        ('failed', 'Thất bại'),
        ('cancelled', 'Đã hủy'),
        ('refunded', 'Đã hoàn tiền'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    fee_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=0)
    
    # Payment gateway details
    gateway_transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    description = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transaction {self.id} - {self.amount:,.0f} VND"

class Deposit(models.Model):
    DEPOSIT_STATUS = [
        ('pending', 'Chờ thanh toán'),
        ('paid', 'Đã thanh toán'),
        ('refunded', 'Đã hoàn tiền'),
        ('forfeited', 'Bị tịch thu'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='deposits')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposits')
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, null=True, blank=True)
    
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    status = models.CharField(max_length=20, choices=DEPOSIT_STATUS, default='pending')
    
    # Refund details
    refund_amount = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    refund_reason = models.TextField(blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Deposit for {self.property.title} - {self.amount:,.0f} VND"