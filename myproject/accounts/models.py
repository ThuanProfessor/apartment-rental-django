from pydoc import describe
from tabnanny import verbose
from django.db import models

from django.contrib.auth.models import AbstractUser
import uuid
from phonenumber_field.modelfields import PhoneNumberField

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('tenant', 'Người thuê'),
        ('landlord', 'Chủ nhà'),
        ('admin', 'Người quản trị'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, default='tenant')
    phone_number = PhoneNumberField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank= True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    is_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False) 
    
    createed_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"(self.username) - {self.get_user_type_display()}"
    

class UserProfile(models.Model):
    user = models.OneToOneRelationship(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextFile(max_length = 50, blank= True)
    facebook_url = models.URLField(blank=True, null=True)
    zalo_number = PhoneNumberField(blank=True, null=True)
    preferred_contact_method = models.CharField(
        max_length=20, 
        choices=[
        
            ('phone', 'Điện thoại'),
            ('email', 'Email'),
            ('facebook', 'Facebook'),
            ('zalo', 'Zalo'),
        ], 
        default='phone'
        
    )
    
    rate = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_review = models.PositiveSmallIntegerField(default=0)
    
    identity_card_number = models.CharField(max_length=20, blank=True, null=True)
    identity_card_front = models.ImageField(upload_to='identity_cards/', blank=True, null=True)
    identity_card_back = models.ImageField(upload_to='identity_cards/', blank=True, null=True)
    is_identity_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Ptofile of {self.user.username}"
    

class OTPVerification(models.Model):
    OTP_TYPE_CHOICES = [
        ('email', 'Email Verification'),
        ('phone', 'Phone Verification'),
        ('password_reset', 'Password Reset'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, choices=OTP_TYPE_CHOICES)
    is_used = models.BooleanField(default=False)
    
    
    createed_at = models.DateTimeField(auto_now_add = True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp_type}"
    
    
class UserActivityLog(models.Model):
    ACTIVITY_CHOICES = [
        ('Login', 'Đăng nhập'),
        ('Logout', 'Đăng xuất'),
        ('view_property', 'Xem căn hộ'),
        ('create_property','Tạo tin đăng'),
        ('update_property', 'Cập nhật tin đăng'),
        ('favoryte_property', 'Yêu thích căn hộ'),
        ('contact_landlord', 'Liên hệ chủ nhà'),
        ('book_viewing', 'Đặt lịch xem nhà'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
    activity_typr = models.Charfield(maxx_length= 50, choices = ACTIVITY_CHOICES)
    description = models.TextField(blank=True, null=True)
    is_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent= models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User Activities'

    
    
    