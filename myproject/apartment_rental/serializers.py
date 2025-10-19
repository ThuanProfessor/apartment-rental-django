from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from .models import CustomUser, Property, PropertyImage, Booking, Review, Contact, Favorite, ViewingSchedule, Payment


class CustomUserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'user_type', 'phone_number', 'avatar', 'date_joined']
        read_only_fields = ['id', 'date_joined']
        ref_name = 'CustomUser'
        extra_kwargs = {
            'phone_number': {'required': False, 'allow_null': True},
            'email': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate_phone_number(self, value):
        # Chấp nhận các dạng, rỗng
        if not value:
            return value
        s = str(value).strip()
        if s.startswith('+84'):
            return s
        if s.startswith('0') and len(s) >= 9:
            return f"+84{s[1:]}"
        # Nếu không đúng định dạng, vẫn trả về để PhoneNumberField xử lý
        return s

    def get_avatar(self, obj):
        try:
            url = obj.avatar.url if obj.avatar else None
            if url:
                return url
        except Exception:
            pass
        try:
            val = getattr(obj, 'avatar', None)
            if not val:
                return None
            if isinstance(val, str) and (val.startswith('http://') or val.startswith('https://')):
                return val
            from cloudinary.utils import cloudinary_url
            url, _ = cloudinary_url(str(val), secure=True)
            return url
        except Exception:
            return None


class PropertyImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'is_main']
        ref_name = 'PropertyImage'

    def get_image(self, obj):
        try:
            return obj.image.url if obj.image else None
        except Exception:
            return None


class PropertySerializer(serializers.ModelSerializer):
    owner = CustomUserSerializer(read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = ['id', 'title', 'description', 'property_type', 'owner',
                 'address', 'district', 'city', 'area', 'bedrooms', 'bathrooms',
                 'price', 'deposit', 'status', 'available_from', 'created_at',
                 'updated_at', 'images', 'is_favorited']
        read_only_fields = ['id', 'created_at', 'updated_at']
        ref_name = 'PropertyDetail'
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False


class PropertyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['title', 'description', 'property_type', 'address', 
                 'district', 'city', 'area', 'bedrooms', 'bathrooms',
                 'price', 'deposit', 'available_from', 'status']
        extra_kwargs = {
            'bedrooms': {'required': False},
            'bathrooms': {'required': False},
            'deposit': {'required': False},
            'available_from': {'required': False},
            'status': {'required': False},
        }
        ref_name = 'PropertyCreate'
    
    def create(self, validated_data):
        #neu khong chon, lay ngay hien tai
        if not validated_data.get('available_from'):
            validated_data['available_from'] = date.today()
        return super().create(validated_data)


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


# Favorite
class FavoriteSerializer(serializers.ModelSerializer):
    property = PropertyListSerializer(read_only=True)
    property_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'property', 'property_id', 'created_at']
        read_only_fields = ['id', 'created_at']
        ref_name = 'Favorite'


# Dashboard
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
    payments = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = ['id', 'property', 'property_id', 'tenant', 'start_date', 
                 'end_date', 'total_amount', 'status', 'notes', 'created_at',
                 'deposit_amount', 'deposit_status', 'deposit_paid_at', 'payments']
        read_only_fields = ['id', 'total_amount', 'created_at', 'deposit_paid_at']
        ref_name = 'Booking'
    
    def create(self, validated_data):
        print(f"DEBUG: validated_data = {validated_data}")
        property_id = validated_data.pop('property_id')
        property_obj = Property.objects.get(id=property_id)
        
       
        days = (validated_data['end_date'] - validated_data['start_date']).days
        months = (Decimal(days) / Decimal(30)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total = (property_obj.price * months).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        validated_data['total_amount'] = total
        validated_data['property'] = property_obj
        
       
        if 'deposit_amount' not in validated_data or validated_data['deposit_amount'] is None:
            print(f"DEBUG: Using property.deposit = {property_obj.deposit}")
            try:
                validated_data['deposit_amount'] = property_obj.deposit
            except Exception:
                validated_data['deposit_amount'] = 0
        else:
            print(f"DEBUG: Using frontend deposit_amount = {validated_data['deposit_amount']}")
        
        print(f"DEBUG: Final validated_data = {validated_data}")
        return super().create(validated_data)

    def get_payments(self, obj):
        qs = getattr(obj, 'payments', None)
        if qs is None:
            return []
        return PaymentSerializer(qs.all(), many=True).data


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



class AgentListSerializer(serializers.ModelSerializer):
    properties_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar', 'properties_count']
        ref_name = 'AgentList'


class ViewingScheduleSerializer(serializers.ModelSerializer):
    property = PropertyListSerializer(read_only=True)
    tenant = CustomUserSerializer(read_only=True)
    property_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = ViewingSchedule
        fields = '__all__'
        ref_name = 'ViewingSchedule'


class PaymentSerializer(serializers.ModelSerializer):
    booking = serializers.PrimaryKeyRelatedField(read_only=True)
    booking_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'booking_id', 'amount', 'provider',
            'vnp_TxnRef', 'vnp_OrderInfo', 'vnp_TransactionNo', 'vnp_ResponseCode',
            'vnp_BankCode', 'vnp_PayDate', 'vnp_SecureHash', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'provider', 'vnp_TxnRef', 'status', 'created_at', 'updated_at']
        ref_name = 'Payment'
    
    def create(self, validated_data):
        booking_id = validated_data.pop('booking_id')
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            raise serializers.ValidationError({'booking_id': 'Booking not found'})
        return Payment.objects.create(booking=booking, provider='vnpay', **validated_data)
