from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from apps.users.models import UserActivityLog
from django.urls import resolve
import json

class RequestValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Sanitize input
        self.sanitize_request(request)
        
        # Check rate limits
        if not self.check_rate_limit(request):
            return JsonResponse({
                "error": "Rate limit exceeded"
            }, status=429)
            
        response = self.get_response(request)
        return response 

class UserActivityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip logging for admin, static and media urls
        path = request.path_info.lstrip('/')
        if path.startswith(('admin/', 'static/', 'media/')):
            return None
            
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                # Get the resolved URL name
                resolver_match = resolve(request.path)
                action = f"{resolver_match.url_name}_{request.method.lower()}"
                
                # Prepare request data for logging
                request_data = {
                    'method': request.method,
                    'path': request.path,
                    'query_params': dict(request.GET),
                }
                
                if request.method in ['POST', 'PUT', 'PATCH']:
                    # Be careful with sensitive data
                    safe_data = self.sanitize_request_data(request.POST)
                    request_data['body'] = safe_data
                
                # Create activity log
                UserActivityLog.objects.create(
                    user=request.user,
                    action=action,
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    action_details=request_data,
                    status='ACTIVE'
                )
            except Exception as e:
                # Log the error but don't block the request
                print(f"Error logging user activity: {str(e)}")
                
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
        
    def sanitize_request_data(self, data):
        """Remove sensitive information from request data"""
        sensitive_fields = ['password', 'token', 'auth', 'key']
        safe_data = {}
        
        for key, value in data.items():
            if any(field in key.lower() for field in sensitive_fields):
                safe_data[key] = '*****'
            else:
                safe_data[key] = value
                
        return safe_data