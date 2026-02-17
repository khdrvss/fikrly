"""Caching utilities for improved performance."""

from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
import hashlib
import json


def cache_per_user(timeout=60 * 5, key_prefix="view"):
    """
    Cache decorator that creates separate cache entries per user.
    Useful for personalized content.

    Args:
        timeout: Cache timeout in seconds (default 5 minutes)
        key_prefix: Prefix for cache key
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Build cache key based on user, path, and query params
            user_id = request.user.id if request.user.is_authenticated else "anon"
            query_string = request.GET.urlencode()
            cache_key = f"{key_prefix}:{user_id}:{request.path}:{query_string}"

            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response

            # Generate response
            response = view_func(request, *args, **kwargs)

            # Cache it
            cache.set(cache_key, response, timeout)

            return response

        return wrapper

    return decorator


def cache_api_response(timeout=60 * 5, vary_on=None):
    """
    Cache decorator specifically for API endpoints returning JSON.

    Args:
        timeout: Cache timeout in seconds
        vary_on: List of request parameter names to include in cache key
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Build cache key
            key_parts = [
                view_func.__name__,
                request.path,
            ]

            # Add vary_on parameters
            if vary_on:
                for param in vary_on:
                    value = request.GET.get(param, "")
                    key_parts.append(f"{param}={value}")

            # Add user authentication state
            if request.user.is_authenticated:
                key_parts.append(f"user={request.user.id}")
            else:
                key_parts.append("anon")

            # Create hash for cleaner key
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            cache_key = f"api:{cache_key}"

            # Try cache
            cached = cache.get(cache_key)
            if cached:
                return JsonResponse(cached)

            # Generate response
            response = view_func(request, *args, **kwargs)

            # Cache JSON data if successful
            if isinstance(response, JsonResponse) and response.status_code == 200:
                try:
                    cache.set(cache_key, json.loads(response.content), timeout)
                except Exception:
                    pass

            return response

        return wrapper

    return decorator


def invalidate_cache_pattern(pattern):
    """
    Invalidate all cache keys matching a pattern.
    Useful when data changes and related caches need clearing.

    Args:
        pattern: Pattern to match (e.g., 'company:*', 'review:123:*')
    """
    try:
        # This works with django-redis backend
        from django_redis import get_redis_connection

        conn = get_redis_connection("default")
        keys = conn.keys(pattern)
        if keys:
            conn.delete(*keys)
            return len(keys)
    except Exception:
        # Fallback for non-redis backends
        pass
    return 0


def warm_cache(keys_and_funcs):
    """
    Pre-populate cache with computed values.

    Args:
        keys_and_funcs: Dict mapping cache keys to callable functions
                       e.g., {'top_companies': lambda: Company.objects.filter(...)}
    """
    for key, func in keys_and_funcs.items():
        try:
            value = func()
            cache.set(key, value, timeout=60 * 60)  # 1 hour default
        except Exception as e:
            print(f"Cache warming failed for {key}: {e}")


class CachedProperty:
    """
    Descriptor for caching expensive property calculations.
    Caches result on instance for request lifetime.
    """

    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__

    def __get__(self, instance, owner):
        if instance is None:
            return self

        # Use instance dict to cache
        attr_name = f"_cached_{self.func.__name__}"
        if not hasattr(instance, attr_name):
            setattr(instance, attr_name, self.func(instance))
        return getattr(instance, attr_name)
