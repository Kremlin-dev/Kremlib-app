from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

# Create a router for our viewsets
router = DefaultRouter()
router.register(r'books', views.BookViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'collections', views.CollectionViewSet)
router.register(r'ratings', views.RatingViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'reading-progress', views.ReadingProgressViewSet)
router.register(r'book-content', views.BookContentViewSet)

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', views.login, name='login'),
    path('auth/signup/', views.register, name='signup'),
    
    # JWT Token management
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/logout-all-devices/', views.invalidate_all_tokens, name='logout_all'),
    
    # Password management
    path('auth/password/request-reset/', views.request_password_reset, name='request_password_reset'),
    path('auth/password/reset/', views.reset_password, name='reset_password'),
    path('auth/password/change/', views.change_password, name='change_password'),
    
    # Legacy endpoints (for backward compatibility)
    path('home/', views.home, name='home'),
    
    # User dashboard
    path('dashboard/', views.UserDashboardView.as_view(), name='user-dashboard'),
    
    # Include all router URLs
    path('api/', include(router.urls)),
]