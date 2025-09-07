import re
from unicodedata import category
from django.db import models

from django.contrib.auth import get_user_model

import uuid
from django.core.validators import MinValueValidator, MaxValueValidator


User = get_user_model()

class PropertyCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'Property Categories'
        
    def __str__(self):
        return self.name


class Amenity(models.Model):
    AMENITY_CATEGORIES = [
        ('basic', 'Cơ bản'),
        ('furniture', 'Nội thất'),
        ('appliance', 'Thiết bị'),
        ('security', 'An ninh'),
        ('entertainment', 'Giải trí'),
        ('transport', 'Giao thông'),
        ('other', 'Khác')
    ]
    
    name = models.CharField(max_length =100, unique=True)
    icon = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=50, choices=AMENITY_CATEGORIES, default='basic')
    is_activate = models.BooleanField(default=True)
    
    class Meta:
        varse_name_plural = 'Amenities'
        
    def __str__(self):
        return self.name

class Property(models.Model):
    PROPERTY_STATUS = [
        ('available', 'Có sẵn'),
        ('rented', 'Đã cho thuê'),
        ('maintenance', 'Bảo trì'),
        ('inactive', 'Không hoạt động'),
        ('pending_approval', 'Chờ duyệt')
    ]    
    
    
    PROPERTY_TYPE = [
        ('apartment', 'Căn hộ'),
        ('house', 'Nhà riêng'),
        ('room', 'Phòng trọ'),
        ('studio', 'Căn hộ Studio'),
        ('villa', 'Biệt thự'),
        ('office', 'Văn phòng')
        
    ]
    
    id = models.UUIDField(primary_key = True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    alug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    property_type = models.Charfile(max_length=20, choices = PROPERTY_TYPE)
    category = models.ForeignKey(PropertyCategory, on_delete=models.SET_NULL, null=True)
    
    owner = models.ForeignKey(User, on_delete= models.CASCADE, related_name='properties')
    
    address = models.TextField()
    ward = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    latutude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    area = models.DecimalField(max_digits=7, decimal_places=2)
    bedroom = models.PositiveIntegerField(default=1)
    bathroom = models.PositiveIntegerField(default=1)
    floor = models.PositiveIntegerField(blank=True, null=True)
    total_floors = models.PositiveIntegerField(blank=True, null=True)
    
    price = models.DecimalField(max_digits=10, decimal_places=0)
    deposit = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    electricity_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    water_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    internet_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    parking_fee = models.Deferrabled(max_digits=10, decimal_places=0, blank=True, null=True)
    
    amenities = models.ManyToManyField(Amenity, blank=True)
    
    status = models.CharField(max_length=20, choices=PROPERTY_STATUS, default='pending_approval')
    available_from = models.DateField()
    minimum_stay = models.PositiveIntegerField(default=1)  # months
    
    # SEO and Analytics
    views_count = models.PositiveIntegerField(default=0)
    favorites_count = models.PositiveIntegerField(default=0)
    contact_count = models.PositiveIntegerField(default=0)
    
    # Admin fields
    is_featured = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.price:,.0f} VND"
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum([review.rating for review in reviews]) / len(reviews)
        return 0

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/')
    caption = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.property.title}"

class PropertyRule(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rules')
    rule_text = models.CharField(max_length=200)
    
    def __str__(self):
        return f"Rule for {self.property.title}: {self.rule_text}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'property']
    
    def __str__(self):
        return f"{self.user.username} favorites {self.property.title}"

class PropertyComparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparisons')
    properties = models.ManyToManyField(Property, related_name='compared_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comparison by {self.user.username}"
        
    