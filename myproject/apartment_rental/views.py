from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import login, logout
from django.db.models import Avg, Count, Sum, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Property, Booking, Review, Contact, CustomUser, Favorite, PropertyImage, ViewingSchedule
from .serializers import (
    PropertySerializer, PropertyListSerializer, PropertyCreateSerializer,
    BookingSerializer, ReviewSerializer, ContactSerializer, CustomUserSerializer,
    UserRegistrationSerializer, UserLoginSerializer, FavoriteSerializer,
    DashboardStatsSerializer, LandlordStatsSerializer, TenantStatsSerializer,
    PropertyImageSerializer, AgentListSerializer, ViewingScheduleSerializer
)

# Firebase Admin imports
import os
try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth
    from firebase_admin import credentials as firebase_credentials
except Exception:
    firebase_admin = None
    firebase_auth = None
    firebase_credentials = None


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property_type', 'district', 'city', 'status', 'owner']
    search_fields = ['title', 'description', 'address']
    ordering_fields = ['price', 'created_at', 'area']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        elif self.action == 'create':
            return PropertyCreateSerializer
        return PropertySerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def create(self, request, *args, **kwargs):
        # Use create serializer for validation, but return full detail with id for client to attach images
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        output = PropertySerializer(instance, context={'request': request})
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def get_queryset(self):
        queryset = Property.objects.select_related('owner').prefetch_related('images')
        
        # Filter available properties for public
        if self.action == 'list' and not self.request.user.is_authenticated:
            queryset = queryset.filter(status='available')
        
        return queryset
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner != request.user:
            return Response({'error': 'Không có quyền chỉnh sửa'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner != request.user:
            return Response({'error': 'Không có quyền chỉnh sửa'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner != request.user:
            return Response({'error': 'Không có quyền xóa'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        property_obj = self.get_object()
        reviews = property_obj.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_images(self, request, pk=None):
        property_obj = self.get_object()
        if property_obj.owner != request.user:
            return Response({'error': 'Không có quyền truy cập'}, status=status.HTTP_403_FORBIDDEN)
        
        images = request.FILES.getlist('images')
        if not images:
            return Response({'error': 'Không có dữ liệu ảnh'}, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_images = []
        for image in images:
            property_image = PropertyImage.objects.create(
                property=property_obj,
                image=image,
                is_main=len(uploaded_images) == 0 and not property_obj.images.exists()
            )
            uploaded_images.append(PropertyImageSerializer(property_image).data)
        
        return Response({'images': uploaded_images}, status=status.HTTP_201_CREATED)
        
        
        
class BookingViewSet(viewsets.ModelViewSet):

    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
        req = getattr(self, 'request', None)
        if not req or not getattr(req, 'user', None) or not req.user.is_authenticated:
            return Booking.objects.none()
        user = req.user
        if getattr(user, 'user_type', None) == 'landlord':
            return Booking.objects.filter(property__owner=user)
        return Booking.objects.filter(tenant=user)
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        req = getattr(self, 'request', None)
        if not req or not getattr(req, 'user', None) or not req.user.is_authenticated:
            return Review.objects.none()
        return Review.objects.filter(reviewer=req.user)
    
    def perform_create(self, serializer):
        property_id = serializer.validated_data.get('property_id')
        property_obj = Property.objects.get(id=property_id)
        serializer.save(reviewer=self.request.user, property=property_obj)


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Contact.objects.none()
        req = getattr(self, 'request', None)
        if not req or not getattr(req, 'user', None) or not req.user.is_authenticated:
            return Contact.objects.none()
        user = req.user
        if getattr(user, 'user_type', None) == 'landlord':
            return Contact.objects.filter(property__owner=user)
        return Contact.objects.filter(tenant=user)
    
    def perform_create(self, serializer):
        property_id = serializer.validated_data.get('property_id')
        property_obj = Property.objects.get(id=property_id)
        serializer.save(tenant=self.request.user, property=property_obj)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        # Allow public access to retrieve agent profile by id or list agents
        if getattr(self, 'action', None) in ['retrieve', 'agents']:
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    def get_queryset(self):
        action = getattr(self, 'action', None)
        # Public profile view (AgentProfile.jsx): allow retrieving any user
        if action == 'retrieve':
            return CustomUser.objects.all()
        # For other actions, only operate on current user
        req = getattr(self, 'request', None)
        if not req or not getattr(req, 'user', None) or not req.user.is_authenticated:
            return CustomUser.objects.none()
        return CustomUser.objects.filter(id=req.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_properties(self, request):
        properties = Property.objects.filter(owner=request.user)
        serializer = PropertyListSerializer(properties, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        bookings = Booking.objects.filter(tenant=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def agents(self, request):
        qs = CustomUser.objects.filter(user_type='landlord').annotate(properties_count=Count('properties'))
        serializer = AgentListSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], url_path='update-profile', parser_classes=[MultiPartParser, FormParser])
    def update_profile(self, request):
        user = request.user

        # Diagnostics (temporarily, to debug 500)
        print(f"update_profile Content-Type: {request.META.get('CONTENT_TYPE')}")
        print(f"update_profile FILES keys: {list(request.FILES.keys())}")

        # Avatar file (optional)
        if 'avatar' in request.FILES:
            avatar_file = request.FILES['avatar']
            try:
                # For CloudinaryField, assign the file and save the model
                user.avatar = avatar_file
                user.save(update_fields=['avatar'])
                print(f"Avatar updated for user {user.username}")
            except Exception as e:
                print(f"Avatar save error: {e}")
                return Response({'error': f'Avatar upload failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Other fields
        try:
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': f'Profile update failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        print(f"Register request data: {request.data}")  # Debug log
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save() #Luu vao sessions
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': CustomUserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
                
            }, status = status.HTTP_201_CREATED)
        
        print(f"Register validation errors: {serializer.errors}")  # Debug log    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': CustomUserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({'message': 'Đăng xuất thành công'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'message': 'Đăng xuất thất bại'}, status=status.HTTP_400_BAD_REQUEST)
            
            

class DashBoardStatsview(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        stats = {
            'total_properties': Property.objects.count(),
            'available_properties': Property.objects.filter(status='available').count(),
            'total_bookings': Booking.objects.count(),
            'pending_bookings': Booking.objects.filter(status='pending').count(),
            'total_reviews': Review.objects.count(),
            'average_rating': Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0,
        }
        
        serializer = DashboardStatsSerializer(stats)
        
        return Response(serializer.data)
    

class DashboardStatsView(DashBoardStatsview):
    pass


class LandlordStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.user_type != 'landlord':
            return Response({'error': 'Không có quyền truy cập'}, status=403)
        
        my_properties = Property.objects.filter(owner=request.user)
        
        bookings = Booking.objects.filter(property__owner=request.user)
        
        stats = {
            
            'my_properties': my_properties.count(),
            'total_bookings': bookings.count(),
            'pending_bookings': bookings.filter(status='pending').count(),
            'confirmed_bookings': bookings.filter(status='confirmed').count(),
            'total_revenue': bookings.filter(status='completed').aggregate(
                total=Sum('total_amount'))['total'] or 0,
            
            'average_rating': Review.objects.filter(
                property__owner=request.user).aggregate(avg=Avg('rating'))['avg'] or 0
        }
        
        serializer = LandlordStatsSerializer(stats)
        
        
        return Response(serializer.data)
        
        

class FileUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        print(f"FileUpload request data: {request.data}")  # Debug log
        print(f"FileUpload request files: {request.FILES}")  # Debug log
        
        # Basic diagnostics
        print(f"Content-Type: {request.META.get('CONTENT_TYPE')}")
        print(f"FILES keys: {list(request.FILES.keys())}")
        
        file_type = (request.data.get('type') or '').strip().lower()
        # If client forgot to send 'type' but there's exactly one file, assume avatar for this endpoint
        if not file_type and len(request.FILES) == 1:
            file_type = 'avatar'
        
        if file_type == 'avatar':
            # Accept common field names and fallback to first file
            avatar_file = (
                request.FILES.get('avatar')
                or request.FILES.get('file')
                or (next(iter(request.FILES.values())) if request.FILES else None)
            )
            print(f"Avatar file: {avatar_file}")  # Debug log
            if not avatar_file:
                return Response({'error': 'Không cung cấp ảnh'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = request.user
            print(f"User: {user.id} - {user.username}")  # Debug log
            
            try:
                # Save directly via Cloudinary-backed DEFAULT_FILE_STORAGE
                # This mirrors how PropertyImage uploads work and avoids manual SDK calls
                user.avatar.save(avatar_file.name, avatar_file, save=True)

                # Build a URL to return
                avatar_url = None
                try:
                    avatar_url = user.avatar.url
                except Exception:
                    # Fallback for safety if direct url access fails
                    try:
                        from cloudinary.utils import cloudinary_url
                        avatar_url, _ = cloudinary_url(str(user.avatar), secure=True)
                    except Exception:
                        avatar_url = None
                
                if not avatar_url:
                    return Response({'error': 'Không thể tạo URL ảnh sau khi upload'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                print(f"Avatar saved, url: {avatar_url}")  # Debug log
                return Response({'avatar_url': avatar_url, 'url': avatar_url}, status=status.HTTP_200_OK)
                
            except Exception as e:
                print(f"Avatar save error: {e}")  # Debug log
                return Response({'error': f'Upload failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif file_type == 'property_image':
            property_id = request.data.get('property_id')
            image = request.FILES.get('image')
            if not property_id or not image:
                return Response({'error': 'Yêu cầu cung cấp ảnh'}, status=status.HTTP_400_BAD_REQUEST)
            # Validate UUID format to avoid 500 when badly formed
            from uuid import UUID
            try:
                pid = UUID(str(property_id))
            except Exception:
                return Response({'error': 'property_id không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                prop = Property.objects.get(id=pid, owner=request.user)
            except Property.DoesNotExist:
                return Response({'error': 'Không tìm thấy hoặc không có quyền'}, status=status.HTTP_404_NOT_FOUND)
            prop_img = PropertyImage.objects.create(property=prop, image=image)
            return Response(PropertyImageSerializer(prop_img).data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'erroe'}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            response.data['message'] = 'Token refreshed successfully'
        return response


class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Lỗi'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Reset password thành công'}, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not old_password or not new_password:
            return Response({'error': 'Yêu cầu nhập mật khẩu'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user.check_password(old_password):
            return Response({'error': 'Mật khẩu cũ không đúng'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Đổi password thành công'}, status=status.HTTP_200_OK)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Favorite.objects.none()
        req = getattr(self, 'request', None)
        if not req or not getattr(req, 'user', None) or not req.user.is_authenticated:
            return Favorite.objects.none()
        return Favorite.objects.filter(user=req.user)
    
    def perform_create(self, serializer):
        property_id = serializer.validated_data.get('property_id')
        property_obj = Property.objects.get(id=property_id)
        serializer.save(user=self.request.user, property=property_obj)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        property_id = request.data.get('property_id')
        try:
            property_obj = Property.objects.get(id=property_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user, 
                property=property_obj
            )
            if not created:
                favorite.delete()
                return Response({'favorited': False})
            return Response({'favorited': True})
        except Property.DoesNotExist:
            return Response({'error': 'Không tìm thấy phòng'}, status=status.HTTP_404_NOT_FOUND)


class TenantStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.user_type != 'tenant':
            return Response({'error': 'Không có quyền truy cập'}, status=status.HTTP_403_FORBIDDEN)
        
        bookings = Booking.objects.filter(tenant=request.user)
        
        stats = {
            
            'my_bookings': bookings.count(),
            'pending_bookings': bookings.filter(status='pending').count(),
            'confirmed_bookings': bookings.filter(status='confirmed').count(),
            'completed_bookings': bookings.filter(status='completed').count(),
            'favorite_properties': Favorite.objects.filter(user=request.user).count(),
            'total_spent': bookings.filter(status='completed').aggregate(
                total=Sum('total_amount'))['total'] or 0
        }
        
        serializer = TenantStatsSerializer(stats)
        
        return Response(serializer.data)


class FirebaseAuthExchangeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        id_token = request.data.get('id_token')
        if not id_token:
            return Response({'error': 'Missing id_token'}, status=status.HTTP_400_BAD_REQUEST)

        if not firebase_admin or not firebase_auth or not firebase_credentials:
            return Response({'error': 'Firebase Admin SDK is not installed on server'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Initialize firebase app if not initialized
        try:
            if not firebase_admin._apps:
                sa_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
                if sa_path and os.path.exists(sa_path):
                    cred = firebase_credentials.Certificate(sa_path)
                else:
                    # Attempt application default credentials
                    cred = firebase_credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)
        except Exception as e:
            return Response({'error': 'Firebase initialization failed', 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            decoded = firebase_auth.verify_id_token(id_token)
            uid = decoded.get('uid')
            email = decoded.get('email')
            name = decoded.get('name') or ''

            # Map or create local user
            user = None
            if email:
                base_username = email.split('@')[0]
                # Ensure unique username by appending uid suffix if needed
                username_candidate = base_username
                if CustomUser.objects.filter(username=username_candidate).exists():
                    username_candidate = f"{base_username}_{uid[:6]}"
                user, _ = CustomUser.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': username_candidate,
                        'first_name': name,
                        'user_type': 'tenant',  # default role
                    }
                )
            else:
                # Phone sign-in may not have email
                username_candidate = f"fb_{uid}"
                if CustomUser.objects.filter(username=username_candidate).exists():
                    username_candidate = f"fb_{uid[:10]}"
                user, _ = CustomUser.objects.get_or_create(
                    username=username_candidate,
                    defaults={
                        'email': '',
                        'first_name': name,
                        'user_type': 'tenant',
                    }
                )

            refresh = RefreshToken.for_user(user)
            return Response({
                'user': CustomUserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'Invalid Firebase token', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ViewingScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ViewingScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'property']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ViewingSchedule.objects.none()
        req = getattr(self, 'request', None)
        if not req or not getattr(req, 'user', None) or not req.user.is_authenticated:
            return ViewingSchedule.objects.none()
        
        # Show viewing schedules for properties owned by user (landlord) or created by user (tenant)
        return ViewingSchedule.objects.filter(
            Q(tenant=req.user) | Q(property__owner=req.user)
        ).select_related('property', 'tenant')
    
    def perform_create(self, serializer):
        property_id = serializer.validated_data.get('property_id')
        if property_id:
            try:
                property_obj = Property.objects.get(id=property_id)
                serializer.save(tenant=self.request.user, property=property_obj)
            except Property.DoesNotExist:
                raise serializers.ValidationError({'property_id': 'Property not found'})
        else:
            serializer.save(tenant=self.request.user)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        schedule = self.get_object()
        if schedule.property.owner != request.user:
            return Response({'error': 'Không có quyền xác nhận'}, status=status.HTTP_403_FORBIDDEN)
        
        confirmed_date = request.data.get('confirmed_date')
        confirmed_time = request.data.get('confirmed_time')
        landlord_response = request.data.get('landlord_response', '')
        
        schedule.status = 'confirmed'
        schedule.confirmed_date = confirmed_date
        schedule.confirmed_time = confirmed_time
        schedule.landlord_response = landlord_response
        schedule.save()
        
        return Response(ViewingScheduleSerializer(schedule).data)