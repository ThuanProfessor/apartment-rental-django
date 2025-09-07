from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class SystemAnalytics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(auto_now_add=True)
    

    total_users = models.IntegerField(default=0)
    total_landlords = models.IntegerField(default=0)
    total_tenants = models.IntegerField(default=0)
    new_users_today = models.IntegerField(default=0)
    

    total_properties = models.IntegerField(default=0)
    available_properties = models.IntegerField(default=0)
    rented_properties = models.IntegerField(default=0)
    new_properties_today = models.IntegerField(default=0)
    

    total_transactions = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    transactions_today = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    

    total_views = models.IntegerField(default=0)
    total_favorites = models.IntegerField(default=0)
    total_messages = models.IntegerField(default=0)
    

    popular_districts = models.JSONField(default=dict)
    average_price_by_district = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "System Analytics"

class PropertyAnalytics(models.Model):
    property = models.OneToOneField('properties.Property', on_delete=models.CASCADE, related_name='analytics')
    

    total_views = models.IntegerField(default=0)
    unique_views = models.IntegerField(default=0)
    views_this_month = models.IntegerField(default=0)
    

    total_favorites = models.IntegerField(default=0)
    total_contacts = models.IntegerField(default=0)
    total_viewing_requests = models.IntegerField(default=0)
    

    viewing_to_application_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    contact_to_viewing_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    

    average_response_time = models.DurationField(null=True, blank=True)
    listing_performance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    updated_at = models.DateTimeField(auto_now=True)

class UserAnalytics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='analytics')
    
    total_logins = models.IntegerField(default=0)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    total_properties_viewed = models.IntegerField(default=0)
    total_properties_favorited = models.IntegerField(default=0)
    

    total_properties_listed = models.IntegerField(default=0)
    total_inquiries_received = models.IntegerField(default=0)
    average_response_time = models.DurationField(null=True, blank=True)
    

    total_viewing_requests = models.IntegerField(default=0)
    total_applications_submitted = models.IntegerField(default=0)
    

    engagement_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    updated_at = models.DateTimeField(auto_now=True)