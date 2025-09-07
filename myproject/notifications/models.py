from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('new_message', 'Tin nhắn mới'),
        ('viewing_request', 'Yêu cầu xem nhà'),
        ('viewing_confirmed', 'Xác nhận lịch xem nhà'),
        ('viewing_cancelled', 'Hủy lịch xem nhà'),
        ('new_review', 'Đánh giá mới'),
        ('property_update', 'Cập nhật tin đăng'),
        ('application_status', 'Trạng thái đơn thuê'),
        ('favorite_update', 'Cập nhật tin yêu thích'),
        ('payment_success', 'Thanh toán thành công'),
        ('payment_failed', 'Thanh toán thất bại'),
        ('property_approved', 'Tin đăng được duyệt'),
        ('property_rejected', 'Tin đăng bị từ chối'),
        ('system_announcement', 'Thông báo hệ thống'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Optional related objects
    related_object_id = models.CharField(max_length=50, null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    action_url = models.URLField(blank=True)
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Push notification tracking
    is_push_sent = models.BooleanField(default=False)
    push_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"

class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notifications
    email_new_message = models.BooleanField(default=True)
    email_viewing_request = models.BooleanField(default=True)
    email_property_update = models.BooleanField(default=False)
    email_marketing = models.BooleanField(default=False)
    
    # Push notifications
    push_new_message = models.BooleanField(default=True)
    push_viewing_request = models.BooleanField(default=True)
    push_property_update = models.BooleanField(default=True)
    
    # SMS notifications
    sms_viewing_confirmed = models.BooleanField(default=False)
    sms_payment_status = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)