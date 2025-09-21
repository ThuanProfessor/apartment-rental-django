from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'apartment_rental'

# API Router for ViewSets
router = DefaultRouter()
router.register(r'properties', views.PropertyViewSet)
router.register(r'bookings', views.BookingViewSet, basename='booking')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'contacts', views.ContactViewSet, basename='contact')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'favorites', views.FavoriteViewSet, basename='favorite')
router.register(r'viewing-schedules', views.ViewingScheduleViewSet, basename='viewing-schedule')

urlpatterns = [
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
  
    path('api/', include(router.urls)),
    
    # Xac thuc
    path('api/auth/register/', views.RegisterView.as_view(), name='register'),
    path('api/auth/login/', views.LoginView.as_view(), name='login'),
    path('api/auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/firebase/', views.FirebaseAuthExchangeView.as_view(), name='firebase_exchange'),
    path('api/auth/password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('api/auth/password-change/', views.PasswordChangeView.as_view(), name='password_change'),
    
    # File
    path('api/upload/', views.FileUploadView.as_view(), name='file_upload'),
    
    # Dashboard
    path('api/dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('api/dashboard/landlord-stats/', views.LandlordStatsView.as_view(), name='landlord-stats'),
    path('api/dashboard/tenant-stats/', views.TenantStatsView.as_view(), name='tenant-stats'),
    
    # DRF
    path('api/auth/', include('rest_framework.urls')),
]
