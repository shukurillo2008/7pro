import time
from django.core.cache import cache
from django.http import HttpResponseForbidden

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        if ip:
            # Key for cache
            key = f"rate_limit_{ip}"
            
            # Get current count
            count = cache.get(key, 0)
            
            if count >= 100:  # Limit: 100 requests per minute
                return HttpResponseForbidden("Too Many Requests. Please try again later.", status=429)
            
            # Increment count and set timeout if new
            if count == 0:
                cache.set(key, 1, 60) # 60 seconds
            else:
                cache.incr(key)
                
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
