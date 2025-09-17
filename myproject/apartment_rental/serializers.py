from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Property, PropertyImage, Booking, Review, Contact, Favorite


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'user_type', 'phone_number', 'avatar', 'date_joined']
        read_only_fields = ['id', 'date_joined']
        ref_name = 'CustomUser'


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'is_main']
        ref_name = 'PropertyImage'


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
        ref_name = 'PropertyDetail'


class PropertyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['title', 'description', 'property_type', 'address', 
                 'district', 'city', 'area', 'bedrooms', 'bathrooms',
                 'price', 'deposit', 'available_from']
        ref_name = 'PropertyCreate'


class PropertyListSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    main_image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = ['id', 'title', 'property_type', 'district', 'city', 
                 'area', 'bedrooms', 'bathrooms', 'price', 'status', 
                 'available_from', 'owner_name', 'main_image', 'is_favorited']
        ref_name = 'PropertyList'
        
    def get_main_image(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return main_image.image.url
        elif obj.images.exists():
            return obj.images.first().image.url
        return None
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)
    password_confirm = serializers.CharField(write_only = True)
    
    class Meta:
        model = CustomUser
        fields =  ['id', 'username', 'email', 'password', 'password_confirm', 
                 'first_name', 'last_name', 'user_type', 'phone_number']
        ref_name = 'UserRegister'
        
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError("Khong the dang nhap voi thong tin nay.")
            if not user.is_active:
                raise serializers.ValidationError("Tai khoan da bi khoa.")
            else:
                attrs['user']=user
                return attrs
        else:
            raise serializers.ValidationError("Phai cung cap du ten dang nhap va mat khau")
        

#Khoi phuc mat khau
class PasswordResetSerializer(serializers.Serializer):
    email  = serializers.EmailField()
    ref_name = 'PasswordReset'


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)
    ref_name = 'ChangePassword'
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    


class PropertyListSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    main_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = ['id', 'title', 'property_type', 'district', 'city', 
                 'area', 'bedrooms', 'bathrooms', 'price', 'status', 
                 'available_from', 'owner_name', 'main_image']
        ref_name = 'PropertyList'
    
    def get_main_image(self, obj):
        main_image = obj.images.filter(is_main=True).first()
        if main_image:
            return main_image.image.url
        elif obj.images.exists():
            return obj.images.first().image.url
        return None


# Authentication Serializers
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password_confirm', 
                 'first_name', 'last_name', 'user_type', 'phone_number']
        ref_name = 'UserRegistration'
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    ref_name = 'UserLogin'
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password')
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    ref_name = 'PasswordReset'


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    ref_name = 'PasswordChange'
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs


# Favorite Serializer
class FavoriteSerializer(serializers.ModelSerializer):
    property = PropertyListSerializer(read_only=True)
    property_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'property', 'property_id', 'created_at']
        read_only_fields = ['id', 'created_at']
        ref_name = 'Favorite'


# Dashboard Statistics Serializers
class DashboardStatsSerializer(serializers.Serializer):
    total_properties = serializers.IntegerField()
    available_properties = serializers.IntegerField()
    total_bookings = serializers.IntegerField()
    pending_bookings = serializers.IntegerField()
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    ref_name = 'DashboardStats'


class LandlordStatsSerializer(serializers.Serializer):
    my_properties = serializers.IntegerField()
    total_bookings = serializers.IntegerField()
    pending_bookings = serializers.IntegerField()
    confirmed_bookings = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=0)
    average_rating = serializers.FloatField()
    ref_name = 'LandlordStats'


class TenantStatsSerializer(serializers.Serializer):
    my_bookings = serializers.IntegerField()
    pending_bookings = serializers.IntegerField()
    confirmed_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
    favorite_properties = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=0)
    ref_name = 'TenantStats'


# thêm mới serializer cho Booking, Review, Contact


class BookingSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    tenant = CustomUserSerializer(read_only=True)
    property_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'property', 'property_id', 'tenant', 'start_date', 
                 'end_date', 'total_amount', 'status', 'notes', 'created_at']
        read_only_fields = ['id', 'total_amount', 'created_at']
        ref_name = 'Booking'
    
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
        ref_name = 'Review'


class ContactSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    tenant = CustomUserSerializer(read_only=True)
    property_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Contact
        fields = ['id', 'property', 'property_id', 'tenant', 'message', 
                 'phone_number', 'created_at']
        read_only_fields = ['id', 'created_at']
        ref_name = 'Contact'
