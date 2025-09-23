from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
import uuid
from ckeditor.fields import RichTextField

from cloudinary.models import CloudinaryField


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('tenant', 'Người thuê'),
        ('landlord', 'Chủ nhà'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='tenant')
    phone_number = PhoneNumberField(blank=True, null=True)
    avatar = CloudinaryField('avatar', blank=True, null=True)
    
    #cấu hình cho phép phân quyền nâng cao trong admin
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_users',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_users',
        blank=True,
    )
    
    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"


class Property(models.Model):
    PROPERTY_TYPE = [
        ('apartment', 'Căn hộ'),
        ('house', 'Nhà riêng'),
        ('room', 'Phòng trọ'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Có sẵn'),
        ('rented', 'Đã cho thuê'),
        ('inactive', 'Không hoạt động'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE)
    
  
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='properties')
    

    address = models.TextField()
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    

    area = models.DecimalField(max_digits=7, decimal_places=2)  # m2
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    

    price = models.DecimalField(max_digits=10, decimal_places=0)  # VND/month
    deposit = models.DecimalField(max_digits=10, decimal_places=0, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    available_from = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.price:,.0f} VND"


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('property_image')
    is_main = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.property.title}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
        ('completed', 'Hoàn thành'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    tenant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    
    # Deposit fields
    DEPOSIT_STATUS = [
        ('none', 'Không đặt cọc'),
        ('pending', 'Đang chờ thanh toán cọc'),
        ('paid', 'Đã đặt cọc'),
        ('failed', 'Thanh toán thất bại'),
        ('refunded', 'Đã hoàn cọc'),
    ]
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    deposit_status = models.CharField(max_length=20, choices=DEPOSIT_STATUS, default='none')
    deposit_paid_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking {self.property.title} by {self.tenant.username}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Đang chờ'),
        ('success', 'Thành công'),
        ('failed', 'Thất bại'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    provider = models.CharField(max_length=30, default='vnpay')
    
    # VNPay specific fields
    vnp_TxnRef = models.CharField(max_length=64, unique=True)
    vnp_OrderInfo = models.CharField(max_length=255, blank=True, null=True)
    vnp_TransactionNo = models.CharField(max_length=64, blank=True, null=True)
    vnp_ResponseCode = models.CharField(max_length=10, blank=True, null=True)
    vnp_BankCode = models.CharField(max_length=50, blank=True, null=True)
    vnp_PayDate = models.CharField(max_length=14, blank=True, null=True)
    vnp_SecureHash = models.CharField(max_length=128, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.vnp_TxnRef} - {self.status}"


class Review(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])  # từ 1 đến 5 sao
    comment = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['property', 'reviewer']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.property.title} - {self.rating} stars"


class Contact(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='contacts')
    tenant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='contacts')
    
    message = models.TextField()
    phone_number = PhoneNumberField()
    
    # Add status tracking for messages
    STATUS_CHOICES = [
        ('unread', 'Chưa đọc'),
        ('read', 'Đã đọc'),
        ('replied', 'Đã trả lời'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Contact for {self.property.title}"


# Viewing Schedule Model for property appointments
class ViewingSchedule(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
        ('completed', 'Hoàn thành'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='viewing_schedules')
    tenant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='viewing_schedules')
    
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    alternative_date = models.DateField(blank=True, null=True)
    alternative_time = models.TimeField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    
    # Response from landlord
    landlord_response = models.TextField(blank=True)
    confirmed_date = models.DateField(blank=True, null=True)
    confirmed_time = models.TimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Viewing {self.property.title} by {self.tenant.username} on {self.preferred_date}"


#Yêu thích
class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'property']
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.property.title}"