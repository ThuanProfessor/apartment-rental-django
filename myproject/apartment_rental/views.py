from urllib import response
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView 
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from sqlalchemy import true
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from .models import Favorite, Property, Booking, Review, Contact, CustomUser
from .serializers import (
    PropertySerializer, PropertyListSerializer, PropertyCreateSerializer,
    BookingSerializer, ReviewSerializer, ContactSerializer, CustomUserSerializer, FavoriteSerializer,
    DashboardStatsSerializer, LandlordStatsSerializer, TenantStatsSerializer, UserRegistrationSerializer
)
from myproject.apartment_rental import serializers


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


class BookingViewSet(viewsets.ModelViewSet):

    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'landlord':
            # Landlords see bookings for their properties
            return Booking.objects.filter(property__owner=user)
        else:
            # Tenants see their own bookings
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
            return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)
        


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        
        if serializer.is_valid:
            user = serializer.save() #Luu vao sessions
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': CustomUserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
                
            }, status = status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            
            
    
    
    
            
        
            
            
            
            
        
            
        
        
    
    

    