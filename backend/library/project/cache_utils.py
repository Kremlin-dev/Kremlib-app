from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings
from functools import wraps
import hashlib
import json


def generate_cache_key(prefix, *args, **kwargs):
    """
    Generate a unique cache key based on the function arguments
    """
    key_parts = [prefix]
    
    # Add positional args to key
    for arg in args:
        if hasattr(arg, 'pk') and arg.pk:
            # For model instances, use their primary key
            key_parts.append(f"{arg.__class__.__name__}_{arg.pk}")
        else:
            # For other types, use their string representation
            key_parts.append(str(arg))
    
    # Add keyword args to key (sorted to ensure consistency)
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key_parts.append(json.dumps(sorted_items))
    
    # Create a hash of the key parts
    key_string = '_'.join(key_parts)
    return f"{settings.CACHE_MIDDLEWARE_KEY_PREFIX}_{hashlib.md5(key_string.encode()).hexdigest()}"


def cache_result(timeout=None):
    """
    Decorator to cache function results
    """
    if timeout is None:
        timeout = settings.CACHE_MIDDLEWARE_SECONDS
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate a unique cache key
            cache_key = generate_cache_key(func.__name__, *args, **kwargs)
            
            # Try to get the result from cache
            result = cache.get(cache_key)
            
            # If not in cache, call the function and cache the result
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
                
            return result
        return wrapper
    return decorator


def invalidate_cache_for(prefix, *args, **kwargs):
    """
    Invalidate cache for a specific function and arguments
    """
    cache_key = generate_cache_key(prefix, *args, **kwargs)
    cache.delete(cache_key)


def invalidate_model_cache(model_name, instance_id=None):
    """
    Invalidate all cache related to a specific model or instance
    """
    if instance_id:
        # If an instance ID is provided, we can be more specific
        pattern = f"{settings.CACHE_MIDDLEWARE_KEY_PREFIX}_{model_name}_{instance_id}"
        keys = [k for k in cache._cache.keys() if pattern in k]
        for key in keys:
            cache.delete(key)
    else:
        # Otherwise, invalidate all cache for the model
        pattern = f"{settings.CACHE_MIDDLEWARE_KEY_PREFIX}_{model_name}"
        keys = [k for k in cache._cache.keys() if pattern in k]
        for key in keys:
            cache.delete(key)


# Method decorator for class-based views
def cache_view_method(timeout=None):
    """
    Decorator for caching class-based view methods
    """
    if timeout is None:
        timeout = settings.CACHE_MIDDLEWARE_SECONDS
        
    def decorator(method):
        @wraps(method)
        def wrapper(self, request, *args, **kwargs):
            # Don't cache for authenticated users with write operations
            if request.method not in ('GET', 'HEAD') or request.user.is_authenticated:
                return method(self, request, *args, **kwargs)
                
            # Generate a cache key
            key_parts = [
                method.__name__,
                request.path,
                request.GET.urlencode()
            ]
            cache_key = f"{settings.CACHE_MIDDLEWARE_KEY_PREFIX}_{'_'.join(key_parts)}"
            
            # Try to get from cache
            response = cache.get(cache_key)
            
            if response is None:
                response = method(self, request, *args, **kwargs)
                cache.set(cache_key, response, timeout)
                
            return response
        return wrapper
    return decorator
