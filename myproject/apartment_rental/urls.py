from curses import ACS_VLINE
from os import name
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views




from rest_framework import permissions
app_name = 'apartment_rental'

# API Router for ViewSets
router = DefaultRouter()
router.register(r'properties', views.PropertyViewSet)
router.register(r'bookings', views.BookingViewSet, basename='booking')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'contacts', views.ContactViewSet, basename='contact')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'favorites', views.FavoriteViewSet, basename='favorite')



urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    path('/api/auth/', include('rest_framework.url')),
    
    path('/api/auth/register/', views.RegisterView.as_view(), name='register'),
    path('/api/auth/login/', views.LoginView.as_view(), name='login'),
    path('/api/auth/logout/', views.LogoutView.as_view(), name='logout'),
    
    path('/api/dashboard/stats/', views.DashBoardStatsview.as_view(), name='dashboard'),
    path('/api/dashboard/landlord-stats/', views.LandlordStatsView.as_view(), name='landlord'),
    path('/api/dashboard/tenant-stats/', views.TenantStatsView.as_view(), name='tenant'),
    
]


