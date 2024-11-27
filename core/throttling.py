from rest_framework.throttling import UserRateThrottle

class CustomUserRateThrottle(UserRateThrottle):
    rate = '100/minute'
    
    def allow_request(self, request, view):
        if request.user.profile.role == ROLE_ADMIN:
            return True
        return super().allow_request(request, view) 

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        } 