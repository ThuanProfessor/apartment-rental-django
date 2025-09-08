from rest_framework import serializers
from .models import CustomUser, Property, PropertyImage, Booking, Review, Contact


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'user_type', 'phone_number', 'avatar', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'is_main']


class PropertySerializer(serializers.ModelSerializer):
    owner = CustomUserSerializer(read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Property
        fields = ['id', 'title', 'description', 'property_type', 'owner',
                 'address', 'district', 'city', 'area', 'bedrooms', 'bathrooms',
                 'price', 'deposit', 'status', 'available_from', 'created_at',
                 'updated_at', 'images']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PropertyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating properties"""
    class Meta:
        model = Property
        fields = ['title', 'description', 'property_type', 'address', 
                 'district', 'city', 'area', 'bedrooms', 'bathrooms',
                 'price', 'deposit', 'available_from']


class BookingSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    tenant = CustomUserSerializer(read_only=True)
    property_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'property', 'property_id', 'tenant', 'start_date', 
                 'end_date', 'total_amount', 'status', 'notes', 'created_at']
        read_only_fields = ['id', 'total_amount', 'created_at']
    
    def create(self, validated_data):
        property_id = validated_data.pop('property_id')
        property_obj = Property.objects.get(id=property_id)
        
        # Calculate total amount
        days = (validated_data['end_date'] - validated_data['start_date']).days
        validated_data['total_amount'] = property_obj.price * (days / 30)
        validated_data['property'] = property_obj
        
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    reviewer = CustomUserSerializer(read_only=True)
    property_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'property', 'property_id', 'reviewer', 'rating', 
                 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']


class ContactSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    tenant = CustomUserSerializer(read_only=True)
    property_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Contact
        fields = ['id', 'property', 'property_id', 'tenant', 'message', 
                 'phone_number', 'created_at']
        read_only_fields = ['id', 'created_at']


# Simplified serializers for list views (better performance)
class PropertyListSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = ['id', 'title', 'property_type', 'district', 'city', 
                 'area', 'bedrooms', 'bathrooms', 'price', 'status', 
                 'available_from', 'owner_name', 'main_image']
    
    def get_main_image(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return main_image.image.url
        elif obj.images.exists():
            return obj.images.first().image.url
        return None
