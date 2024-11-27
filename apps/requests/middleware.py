from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

class RequestMiddleware:
    """
    Middleware for handling request-related functionality
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        
        # Add request tracking for authenticated users
        if hasattr(request, 'user') and not isinstance(request.user, AnonymousUser):
            request.user.last_activity = timezone.now()
            if hasattr(request.user, 'profile'):
                request.user.profile.save()  # This will update the last_modified timestamp

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Called just before Django calls the view.
        """
        # Add any request-specific processing here
        return None

    def process_exception(self, request, exception):
        """
        Called when a view raises an exception.
        """
        # Log any request-related exceptions here
        return None

    def process_template_response(self, request, response):
        """
        Called just after the view has finished executing, if the response
        contains a render() method
        """
        # Add any template-specific processing here
        return response 