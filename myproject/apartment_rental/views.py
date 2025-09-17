from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import login, logout
from django.db.models import Avg, Count, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from sqlalchemy import exists
from .models import Property, Booking, Review, Contact, CustomUser, Favorite, PropertyImage
from .serializers import (
    PropertySerializer, PropertyListSerializer, PropertyCreateSerializer,
    BookingSerializer, ReviewSerializer, ContactSerializer, CustomUserSerializer,
    UserRegistrationSerializer, UserLoginSerializer, FavoriteSerializer,
    DashboardStatsSerializer, LandlordStatsSerializer, TenantStatsSerializer,
    PropertyImageSerializer
)
from . import serializers


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property_type', 'district', 'city', 'status']
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
    
    
    def get_queryset(self):
        queryset = Property.objects.select_related('owner').prefetch_related('images')
        if self.action == 'list' and not self.request.user.is_authenticated:
            queryset = queryset.filter(status='available')
        
        return queryset
    
        
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        property_obj = self.get_object()
        reviews = property_obj.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['property_type', 'district', 'city', 'status']
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
    
    def get_queryset(self):
        queryset = Property.objects.select_related('owner').prefetch_related('images')
        
        # Filter available properties for public
        if self.action == 'list' and not self.request.user.is_authenticated:
            queryset = queryset.filter(status='available')
        
        return queryset
    
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
            return Response({'error': 'PKhong co quyen truy cap'}, status=status.HTTP_403_FORBIDDEN)
        
        images = request.FILES.getlist('images')
        if not images:
            return Response({'error': 'Khong co du lieu anh'}, status=status.HTTP_400_BAD_REQUEST)
        
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
        user = self.request.user
        if user.user_type == 'landlord':
            return Booking.objects.filter(property__owner=user)
        else:
            return Booking.objects.filter(tenant=user)
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(reviewer=self.request.user)
    
    def perform_create(self, serializer):
        property_id = serializer.validated_data.get('property_id')
        property_obj = Property.objects.get(id=property_id)
        serializer.save(reviewer=self.request.user, property=property_obj)


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'landlord':
            return Contact.objects.filter(property__owner=user)
        else:
            return Contact.objects.filter(tenant=user)
    
    def perform_create(self, serializer):
        property_id = serializer.validated_data.get('property_id')
        property_obj = Property.objects.get(id=property_id)
        serializer.save(tenant=self.request.user, property=property_obj)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_properties(self, request):
        properties = Property.objects.filter(owner=request.user)
        serializer = PropertyListSerializer(properties, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        bookings = Booking.objects.filter(tenant=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class FavoriteViewSet(viewsets.ViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.objects.filter(user=self.request.user)
    
    
    def perform_create(self, serializer):
        property_id = serializer.validated_data.get('property_id')
        property_obj = Property.objects.get(id=property_id)
        serializer.save(user=self.request.user, property=property_obj)
        
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        property_id = request.data.get('property_id')
        
        try:
            property_obj = Property.objects.get(id=property_id)
            favorite, created = Favorite.objects.add_or_create(
                user = request.user,
                property = property_obj
            )
            
            if not created:
                favorite.delete()
                return Response({'favorited': False})
            return Response({'favorited': True})
        
        except Property.DoesNotExist:
            return Response({'error': 'Khong co phong'}, status=status.HTTP_404_NOT_FOUND)
        


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        
        if serializer.is_valid():
            user = serializer.save() #Luu vao sessions
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': CustomUserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
                
            }, status = status.HTTP_201_CREATED)
            
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
            'total_booking': Booking.objects.count(),
            'pending_booking': Booking.objects.filter(status='pending').count(),
            'total_review': Review.objects.count(),
            'avg_rating': Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0
            
             
        }
        
        serializer = DashboardStatsSerializer(stats)
        
        return Response(serializer.data)
    

class DashboardStatsView(DashBoardStatsview):
    pass


class LandlordStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.user_type != 'landlord':
            return Response({'error': 'Khong co quyen truy cap'}, status=403)
        
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
        file_type = request.data.get('type')
        if file_type == 'avatar':
            avatar = request.FILES.get('avatar')
            if not avatar:
                return Response({'error': 'Khong cung cap avt'}, status=status.HTTP_400_BAD_REQUEST)
            user = request.user
            user.avatar = avatar
            user.save()
            return Response({'avatar_url': user.avatar.url if user.avatar else None}, status=status.HTTP_200_OK)
        elif file_type == 'property_image':
            property_id = request.data.get('property_id')
            image = request.FILES.get('image')
            if not property_id or not image:
                return Response({'error': 'Yeu cau cap images'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                prop = Property.objects.get(id=property_id, owner=request.user)
            except Property.DoesNotExist:
                return Response({'error': 'Khong tim thay'}, status=status.HTTP_404_NOT_FOUND)
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
            return Response({'error': 'Loi'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Reset password thanh cong'}, status=status.HTTP_200_OK)


class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not old_password or not new_password:
            return Response({'error': 'Yeu cau nhap mat khau'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user.check_password(old_password):
            return Response({'error': 'Mat khau cu khong dung'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Doi password thanh cong'}, status=status.HTTP_200_OK)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    
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
            return Response({'error': 'Khong tim thay phong'}, status=status.HTTP_404_NOT_FOUND)


class TenantStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.user_type != 'tenant':
            return Response({'error': 'Khong co quyen truy cap'}, status=status.HTTP_403_FORBIDDEN)
        
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