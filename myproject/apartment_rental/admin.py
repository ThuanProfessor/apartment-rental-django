from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Property, PropertyImage, Booking, Review, Contact


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'phone_number', 'is_active')
    list_filter = ('user_type', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'phone_number')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'phone_number', 'avatar')
        }),
    )


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'property_type', 'price', 'status', 'created_at')
    list_filter = ('property_type', 'status', 'city', 'district')
    search_fields = ('title', 'address', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PropertyImageInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'property_type', 'owner')
        }),
        ('Location', {
            'fields': ('address', 'district', 'city')
        }),
        ('Details', {
            'fields': ('area', 'bedrooms', 'bathrooms')
        }),
        ('Pricing', {
            'fields': ('price', 'deposit')
        }),
        ('Status', {
            'fields': ('status', 'available_from')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('property', 'tenant', 'start_date', 'end_date', 'total_amount', 'status')
    list_filter = ('status', 'start_date', 'created_at')
    search_fields = ('property__title', 'tenant__username')
    readonly_fields = ('created_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('property', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('property__title', 'reviewer__username', 'comment')
    readonly_fields = ('created_at',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('property', 'tenant', 'phone_number', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('property__title', 'tenant__username', 'message')
    readonly_fields = ('created_at',)
