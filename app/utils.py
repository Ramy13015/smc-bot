"""
Utility functions for anti-duplicate detection and caching
"""
import time
from typing import Dict, Set

# In-memory cache for duplicate detection
_cache: Dict[str, float] = {}


def is_duplicate(event_id: str, ttl_seconds: int = 300) -> bool:
    """
    Check if event_id is a duplicate within TTL window
    
    Args:
        event_id: Unique event identifier
        ttl_seconds: Time-to-live in seconds
        
    Returns:
        True if duplicate, False if new
    """
    current_time = time.time()
    
    # Clean expired entries
    _cleanup_cache(current_time, ttl_seconds)
    
    # Check if event exists
    if event_id in _cache:
        return True
    
    # Add new event
    _cache[event_id] = current_time
    return False


def _cleanup_cache(current_time: float, ttl_seconds: int) -> None:
    """
    Remove expired entries from cache
    
    Args:
        current_time: Current timestamp
        ttl_seconds: Time-to-live in seconds
    """
    expired_keys = [
        key for key, timestamp in _cache.items()
        if current_time - timestamp > ttl_seconds
    ]
    
    for key in expired_keys:
        del _cache[key]


def clear_cache() -> None:
    """Clear all entries from cache"""
    _cache.clear()


def get_cache_size() -> int:
    """Get current cache size"""
    return len(_cache)


def get_cache_keys() -> Set[str]:
    """Get all cache keys"""
    return set(_cache.keys())