from django.http import HttpResponseForbidden
from django.conf import settings
import ipaddress


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def is_internal_ip(client_ip):
    """Check if IP is in the allowed internal IPs"""
    try:
        client = ipaddress.ip_address(client_ip)
        for allowed_ip in settings.INTERNAL_SERVICE_IPS:
            if client == ipaddress.ip_address(allowed_ip):
                return True

        # Also check for private networks in development
        if settings.DEBUG:
            return client.is_private

    except ValueError:
        return False

    return False


def is_internal_request(request):
    """Check if the request is from an internal service"""
    client_ip = get_client_ip(request)
    if is_internal_ip(client_ip):
        return True
    return False
