"""Cache utilities for CRM API endpoints."""
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar

# Type variable for the return type of the cached function
T = TypeVar('T')

# In-memory cache storage
# Structure: {key: (value, expiry_time)}
_cache: Dict[str, tuple[Any, datetime]] = {}

def cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a cache key from the function arguments.
    
    Args:
        prefix: A prefix for the cache key (usually the function name)
        *args: Positional arguments to the function
        **kwargs: Keyword arguments to the function
        
    Returns:
        A string key for the cache
    """
    # Convert args and kwargs to strings and join them
    args_str = '_'.join(str(arg) for arg in args if arg is not None)
    kwargs_str = '_'.join(f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None)
    
    # Combine prefix with args and kwargs
    key_parts = [prefix]
    if args_str:
        key_parts.append(args_str)
    if kwargs_str:
        key_parts.append(kwargs_str)
    
    return ':'.join(key_parts)

def cached(ttl_seconds: int = 300):
    """
    Decorator to cache the result of a function.
    
    Args:
        ttl_seconds: Time to live in seconds for the cached result
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            # Generate cache key
            key = cache_key(func.__name__, *args, **kwargs)
            
            # Check if result is in cache and not expired
            if key in _cache:
                value, expiry = _cache[key]
                if datetime.now() < expiry:
                    return value
            
            # Call the function and cache the result
            result = await func(*args, **kwargs)
            _cache[key] = (result, datetime.now() + timedelta(seconds=ttl_seconds))
            return result
        
        return wrapper
    
    return decorator

def invalidate_cache(prefix: Optional[str] = None):
    """
    Invalidate cache entries.
    
    Args:
        prefix: If provided, only invalidate entries with this prefix
    """
    global _cache
    
    if prefix is None:
        # Invalidate all cache entries
        _cache = {}
    else:
        # Invalidate only entries with the given prefix
        _cache = {k: v for k, v in _cache.items() if not k.startswith(f"{prefix}:")}

def get_cache_stats():
    """
    Get statistics about the cache.
    
    Returns:
        Dictionary with cache statistics
    """
    now = datetime.now()
    total_entries = len(_cache)
    valid_entries = sum(1 for _, expiry in _cache.values() if expiry > now)
    expired_entries = total_entries - valid_entries
    
    return {
        "total_entries": total_entries,
        "valid_entries": valid_entries,
        "expired_entries": expired_entries,
        "memory_usage_bytes": _estimate_memory_usage(),
    }

def _estimate_memory_usage() -> int:
    """
    Estimate the memory usage of the cache in bytes.
    
    Returns:
        Estimated memory usage in bytes
    """
    import sys
    
    # This is a rough estimate
    return sum(sys.getsizeof(k) + sys.getsizeof(v[0]) for k, v in _cache.items())
