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
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking {self.property.title} by {self.tenant.username}"


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
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Contact for {self.property.title}"
