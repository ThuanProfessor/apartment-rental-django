from django.db import models
from django.contrib.auth import get_user_model
from properties.models import Property
import uuid

User = get_user_model()

class ViewingSchedule(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('completed', 'Đã hoàn thành'),
        ('cancelled', 'Đã hủy'),
        ('no_show', 'Không đến'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='viewing_schedules')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewing_requests')
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewing_appointments')
    
    scheduled_date = models.DateTimeField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
  
    tenant_phone = models.CharField(max_length=15)
    tenant_notes = models.TextField(blank=True)
    landlord_notes = models.TextField(blank=True)
    
   
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"Viewing {self.property.title} by {self.tenant.username}"

class RentalApplication(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Đã nộp đơn'),
        ('under_review', 'Đang xem xét'),
        ('approved', 'Đã chấp thuận'),
        ('rejected', 'Đã từ chối'),
        ('withdrawn', 'Đã rút đơn'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='applications')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rental_applications')
    
   
    move_in_date = models.DateField()
    rental_period = models.PositiveIntegerField()  # months
    monthly_income = models.DecimalField(max_digits=12, decimal_places=0)
    occupation = models.CharField(max_length=100)
    employer = models.CharField(max_length=100, blank=True)
    
  
    reference_name = models.CharField(max_length=100, blank=True)
    reference_phone = models.CharField(max_length=15, blank=True)
    reference_relationship = models.CharField(max_length=50, blank=True)
    
   
    income_proof = models.FileField(upload_to='applications/income_proof/', blank=True, null=True)
    employment_letter = models.FileField(upload_to='applications/employment/', blank=True, null=True)
    
    additional_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    
   
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Application for {self.property.title} by {self.tenant.username}"
