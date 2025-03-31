from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .utils import standard_response


class TokenManager:
    """
    A utility class to handle token operations like blacklisting, refreshing, and validation.
    """
    
    @staticmethod
    def blacklist_token(token):
        """
        Blacklist a refresh token to prevent its future use
        """
        try:
            token = RefreshToken(token)
            token.blacklist()
            return True, None
        except TokenError as e:
            return False, str(e)
    
    @staticmethod
    def validate_token(token):
        """
        Validate a token without blacklisting it
        """
        try:
            RefreshToken(token)
            return True, None
        except TokenError as e:
            return False, str(e)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout a user by blacklisting their refresh token
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return standard_response(
            message="Refresh token is required",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    success, error = TokenManager.blacklist_token(refresh_token)
    
    if success:
        # Update last_logout timestamp if UserProfile has this field
        try:
            profile = request.user.profile
            profile.last_logout = timezone.now()
            profile.save(update_fields=['last_logout'])
        except:
            # If profile doesn't exist or doesn't have last_logout field, just continue
            pass
            
        return standard_response(
            message="Successfully logged out",
            status_code=status.HTTP_200_OK
        )
    else:
        return standard_response(
            message="Invalid token",
            errors={"detail": error},
            status_code=status.HTTP_400_BAD_REQUEST
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def invalidate_all_tokens(request):
    """
    Invalidate all tokens for a user (logout from all devices)
    """
    user = request.user
    
    # Get all valid tokens for user and blacklist them
    RefreshToken.for_user(user)
    
    # Update last_logout timestamp if UserProfile has this field
    try:
        profile = user.profile
        profile.last_logout = timezone.now()
        profile.save(update_fields=['last_logout'])
    except:
        # If profile doesn't exist or doesn't have last_logout field, just continue
        pass
        
    return standard_response(
        message="Successfully logged out from all devices",
        status_code=status.HTTP_200_OK
    )
