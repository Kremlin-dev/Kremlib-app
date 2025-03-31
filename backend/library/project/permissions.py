from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsBookOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a book to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the uploader
        return obj.uploaded_by == request.user


class IsProfileOwner(permissions.BasePermission):
    """
    Custom permission to only allow users to edit their own profile.
    """
    
    def has_object_permission(self, request, view, obj):
        # Only allow access to the user's own profile
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit, but anyone can read.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff
