"""
URL configuration for library project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from project.admin import siteadmin

# Import for Swagger documentation
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Kremlib API",
        default_version='v1',
        description="""
        # Kremlib Library Application API
        
        This API provides endpoints for managing books, user profiles, collections, ratings, comments, and reading progress.
        
        ## Authentication
        Most endpoints require authentication using JWT tokens. To authenticate:
        1. Obtain a token pair by sending credentials to `/auth/login/`
        2. Include the access token in the Authorization header: `Bearer <token>`
        3. Refresh expired tokens using `/auth/token/refresh/`
        4. Logout by blacklisting tokens with `/auth/logout/`
        
        ## Features
        - Book management: upload, download, read online, search, filter
        - User profiles: registration, preferences, reading analytics
        - Collections: create personal book collections
        - Social features: ratings, comments, recommendations
        - Reading progress tracking
        """,
        terms_of_service="https://www.kremlib.com/terms/",
        contact=openapi.Contact(email="contact@kremlib.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", siteadmin.urls),
    path("", include('project.urls')),
    
    # Swagger documentation URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
