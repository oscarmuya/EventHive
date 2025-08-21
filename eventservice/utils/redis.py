import redis, json, logging
from typing import Any, Optional, Dict, List
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Redis client wrapper with helper methods for common operations
    """

    def __init__(self):
        """Initialize Redis connection"""
        self.redis_client = redis.Redis(
            host=getattr(settings, "REDIS_HOST", "localhost"),
            port=getattr(settings, "REDIS_PORT", 6379),
            db=getattr(settings, "REDIS_DB", 0),
            password=getattr(settings, "REDIS_PASSWORD", None),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )

    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        try:
            self.redis_client.ping()
            return True
        except redis.ConnectionError:
            logger.error("Redis connection failed")
            return False

    # Basic Key-Value Operations
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a key-value pair with optional TTL

        Args:
            key: Redis key
            value: Value to store (will be JSON serialized)
            ttl: Time to live in seconds
        """
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, cls=DjangoJSONEncoder)
            elif not isinstance(value, str):
                value = str(value)

            if ttl:
                return self.redis_client.setex(key, ttl, value)
            return self.redis_client.set(key, value)
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get value by key with optional default"""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return default

            # Try to parse as JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return default

    def delete(self, *keys: str) -> int:
        """Delete one or more keys"""
        try:
            return self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE error for keys {keys}: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key"""
        try:
            return self.redis_client.expire(key, ttl)
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False

    def ttl(self, key: str) -> int:
        """Get TTL for key"""
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return -1

    # Hash Operations
    def hset(self, name: str, mapping: Dict[str, Any]) -> int:
        """Set hash fields"""
        try:
            # Convert dict values to JSON strings
            serialized_mapping = {}
            for k, v in mapping.items():
                if isinstance(v, (dict, list)):
                    serialized_mapping[k] = json.dumps(v, cls=DjangoJSONEncoder)
                else:
                    serialized_mapping[k] = str(v)
            return self.redis_client.hset(name, mapping=serialized_mapping)
        except Exception as e:
            logger.error(f"Redis HSET error for hash {name}: {e}")
            return 0

    def hget(self, name: str, key: str, default: Any = None) -> Any:
        """Get hash field value"""
        try:
            value = self.redis_client.hget(name, key)
            if value is None:
                return default

            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis HGET error for hash {name}, key {key}: {e}")
            return default

    def hgetall(self, name: str) -> Dict[str, Any]:
        """Get all hash fields and values"""
        try:
            data = self.redis_client.hgetall(name)
            result = {}
            for k, v in data.items():
                try:
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    result[k] = v
            return result
        except Exception as e:
            logger.error(f"Redis HGETALL error for hash {name}: {e}")
            return {}

    def hdel(self, name: str, *keys: str) -> int:
        """Delete hash fields"""
        try:
            return self.redis_client.hdel(name, *keys)
        except Exception as e:
            logger.error(f"Redis HDEL error for hash {name}: {e}")
            return 0

    def hexists(self, name: str, key: str) -> bool:
        """Check if hash field exists"""
        try:
            return bool(self.redis_client.hexists(name, key))
        except Exception as e:
            logger.error(f"Redis HEXISTS error for hash {name}, key {key}: {e}")
            return False

    # List Operations
    def lpush(self, name: str, *values: Any) -> int:
        """Push values to left of list"""
        try:
            serialized_values = []
            for v in values:
                if isinstance(v, (dict, list)):
                    serialized_values.append(json.dumps(v, cls=DjangoJSONEncoder))
                else:
                    serialized_values.append(str(v))
            return self.redis_client.lpush(name, *serialized_values)
        except Exception as e:
            logger.error(f"Redis LPUSH error for list {name}: {e}")
            return 0

    def rpush(self, name: str, *values: Any) -> int:
        """Push values to right of list"""
        try:
            serialized_values = []
            for v in values:
                if isinstance(v, (dict, list)):
                    serialized_values.append(json.dumps(v, cls=DjangoJSONEncoder))
                else:
                    serialized_values.append(str(v))
            return self.redis_client.rpush(name, *serialized_values)
        except Exception as e:
            logger.error(f"Redis RPUSH error for list {name}: {e}")
            return 0

    def lpop(self, name: str) -> Any:
        """Pop value from left of list"""
        try:
            value = self.redis_client.lpop(name)
            if value is None:
                return None

            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis LPOP error for list {name}: {e}")
            return None

    def rpop(self, name: str) -> Any:
        """Pop value from right of list"""
        try:
            value = self.redis_client.rpop(name)
            if value is None:
                return None

            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis RPOP error for list {name}: {e}")
            return None

    def lrange(self, name: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get list range"""
        try:
            values = self.redis_client.lrange(name, start, end)
            result = []
            for v in values:
                try:
                    result.append(json.loads(v))
                except (json.JSONDecodeError, TypeError):
                    result.append(v)
            return result
        except Exception as e:
            logger.error(f"Redis LRANGE error for list {name}: {e}")
            return []

    def llen(self, name: str) -> int:
        """Get list length"""
        try:
            return self.redis_client.llen(name)
        except Exception as e:
            logger.error(f"Redis LLEN error for list {name}: {e}")
            return 0

    # Set Operations
    def sadd(self, name: str, *values: Any) -> int:
        """Add values to set"""
        try:
            serialized_values = []
            for v in values:
                if isinstance(v, (dict, list)):
                    serialized_values.append(json.dumps(v, cls=DjangoJSONEncoder))
                else:
                    serialized_values.append(str(v))
            return self.redis_client.sadd(name, *serialized_values)
        except Exception as e:
            logger.error(f"Redis SADD error for set {name}: {e}")
            return 0

    def srem(self, name: str, *values: Any) -> int:
        """Remove values from set"""
        try:
            serialized_values = []
            for v in values:
                if isinstance(v, (dict, list)):
                    serialized_values.append(json.dumps(v, cls=DjangoJSONEncoder))
                else:
                    serialized_values.append(str(v))
            return self.redis_client.srem(name, *serialized_values)
        except Exception as e:
            logger.error(f"Redis SREM error for set {name}: {e}")
            return 0

    def smembers(self, name: str) -> set:
        """Get all set members"""
        try:
            values = self.redis_client.smembers(name)
            result = set()
            for v in values:
                try:
                    result.add(json.loads(v))
                except (json.JSONDecodeError, TypeError):
                    result.add(v)
            return result
        except Exception as e:
            logger.error(f"Redis SMEMBERS error for set {name}: {e}")
            return set()

    def sismember(self, name: str, value: Any) -> bool:
        """Check if value is in set"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, cls=DjangoJSONEncoder)
            else:
                value = str(value)
            return bool(self.redis_client.sismember(name, value))
        except Exception as e:
            logger.error(f"Redis SISMEMBER error for set {name}: {e}")
            return False

    # Cache Operations
    def cache_set(self, key: str, value: Any, timeout: int = 3600) -> bool:
        """Cache a value with timeout (default 1 hour)"""
        cache_key = f"cache:{key}"
        return self.set(cache_key, value, timeout)

    def cache_get(self, key: str, default: Any = None) -> Any:
        """Get cached value"""
        cache_key = f"cache:{key}"
        return self.get(cache_key, default)

    def cache_delete(self, key: str) -> bool:
        """Delete cached value"""
        cache_key = f"cache:{key}"
        return bool(self.delete(cache_key))

    def cache_get_or_set(self, key: str, callable_func, timeout: int = 3600) -> Any:
        """Get from cache or set if not exists"""
        cache_key = f"cache:{key}"
        cached_value = self.get(cache_key)

        if cached_value is not None:
            return cached_value

        # Get fresh value
        fresh_value = callable_func()
        self.set(cache_key, fresh_value, timeout)
        return fresh_value

    # Session Operations
    def set_session(
        self, session_id: str, user_id: int, data: Dict[str, Any], ttl: int = 86400
    ) -> bool:
        """Set user session data (default 24 hours)"""
        session_key = f"session:{session_id}"
        session_data = {
            "user_id": user_id,
            "data": data,
            "created_at": json.dumps(timezone.now(), cls=DjangoJSONEncoder),
        }
        return self.set(session_key, session_data, ttl)

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get user session data"""
        session_key = f"session:{session_id}"
        return self.get(session_key)

    def delete_session(self, session_id: str) -> bool:
        """Delete user session"""
        session_key = f"session:{session_id}"
        return bool(self.delete(session_key))

    # Rate Limiting
    def rate_limit_check(
        self, identifier: str, limit: int, window: int
    ) -> Dict[str, Any]:
        """
        Check rate limit for identifier

        Args:
            identifier: Unique identifier (user_id, IP, etc.)
            limit: Number of requests allowed
            window: Time window in seconds

        Returns:
            Dict with 'allowed', 'remaining', 'reset_time'
        """
        key = f"rate_limit:{identifier}"
        current_time = int(time.time())

        try:
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, current_time - window)
            pipe.zcard(key)
            pipe.zadd(key, {current_time: current_time})
            pipe.expire(key, window)
            results = pipe.execute()

            current_requests = results[1]

            if current_requests < limit:
                return {
                    "allowed": True,
                    "remaining": limit - current_requests - 1,
                    "reset_time": current_time + window,
                }
            else:
                # Remove the request we just added since it's over limit
                self.redis_client.zrem(key, current_time)
                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset_time": current_time + window,
                }

        except Exception as e:
            logger.error(f"Rate limit check error for {identifier}: {e}")
            return {
                "allowed": True,
                "remaining": limit,
                "reset_time": current_time + window,
            }

    # Utility Methods
    def flush_all(self) -> bool:
        """Flush all Redis data (use with caution!)"""
        try:
            return self.redis_client.flushall()
        except Exception as e:
            logger.error(f"Redis FLUSHALL error: {e}")
            return False

    def get_keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern"""
        try:
            return self.redis_client.keys(pattern)
        except Exception as e:
            logger.error(f"Redis KEYS error for pattern {pattern}: {e}")
            return []

    def get_info(self) -> Dict[str, Any]:
        """Get Redis server info"""
        try:
            return self.redis_client.info()
        except Exception as e:
            logger.error(f"Redis INFO error: {e}")
            return {}


# Global instance
redis_client = RedisClient()


# Convenience functions
def cache_view_data(
    view_name: str, params: Dict[str, Any], data: Any, timeout: int = 3600
) -> bool:
    """Cache view data with automatic key generation"""
    cache_key = f"view:{view_name}:{hash(str(sorted(params.items())))}"
    return redis_client.cache_set(cache_key, data, timeout)


def get_cached_view_data(
    view_name: str, params: Dict[str, Any], default: Any = None
) -> Any:
    """Get cached view data"""
    cache_key = f"view:{view_name}:{hash(str(sorted(params.items())))}"
    return redis_client.cache_get(cache_key, default)


def cache_queryset(
    queryset_key: str, queryset_data: List[Dict], timeout: int = 1800
) -> bool:
    """Cache queryset results (default 30 minutes)"""
    return redis_client.cache_set(f"queryset:{queryset_key}", queryset_data, timeout)


def get_cached_queryset(queryset_key: str, default: List = None) -> List[Dict]:
    """Get cached queryset"""
    if default is None:
        default = []
    return redis_client.cache_get(f"queryset:{queryset_key}", default)


# Import required modules for session operations
try:
    from django.utils import timezone
    import time
except ImportError:
    pass
