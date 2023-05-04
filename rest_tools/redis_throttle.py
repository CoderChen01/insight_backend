from rest_framework.throttling import SimpleRateThrottle

from rest_tools.redis_operations import RedisThrottleCache


class SendMailThrottle(SimpleRateThrottle):
    cache = RedisThrottleCache
    scope = "email"

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self.get_ident(request),
        }
