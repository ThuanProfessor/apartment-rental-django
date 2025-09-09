from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'apartment_rental'

# API Router for ViewSets
router = DefaultRouter()
router.register(r'properties', views.PropertyViewSet)
router.register(r'bookings', views.BookingViewSet, basename='booking')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'contacts', views.ContactViewSet, basename='contact')
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # Authentication endpoints (using DRF's built-in)
    path('api/auth/', include('rest_framework.urls')),
    
]
