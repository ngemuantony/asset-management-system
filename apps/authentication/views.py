from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator 
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, views
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework.parsers import JSONParser
import json
from django.utils.encoding import force_bytes
from django.conf import settings
import logging

from apps.authentication.serializers import (
     PasswordResetConfirmSerializer, PasswordResetRequestSerializer,
     RegisterSerializer, PasswordChangeSerializer,
     LoginSerializer
)
from core.monitoring import AuthenticationMonitor

# Configure logger
logger = logging.getLogger(__name__)

# ============================== AUTHENTICATION MODULES =============================
class RegisterView(APIView):
    """
    Register a new user in the system.
    
    Accepts POST requests with user registration data and creates a new user account.
    """
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    @transaction.atomic
    def post(self, request):
        """
        Create a new user account.

        Parameters:
            username (str): Unique username for the account
            email (str): Valid email address
            password (str): Password meeting minimum requirements
            firstName (str): User's first name
            lastName (str): User's last name

        Returns:
            Response with user data and success message if registration is successful.
            Error response with validation errors if registration fails.
        """
        try:
            # Log the incoming data for debugging
            print("Received data:", request.data)
            
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Registration successful",
                    "user": serializer.data
                }, status=status.HTTP_201_CREATED)
            
            # Return validation errors
            return Response({
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except json.JSONDecodeError as e:
            return Response({
                "message": "Invalid JSON format",
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "message": "An error occurred",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]
    throttle_scope = 'login'

    def initialize_cache_metrics(self):
        """Initialize cache metrics if they don't exist"""
        metrics = {
            'active_sessions': 'active_sessions',
            'failed_attempts': 'failed_attempts',
            'auth_response_time': 'auth_response_time',
            'token_refresh_count': 'token_refresh_count',
            'concurrent_users': 'concurrent_users'
        }
        
        for key in metrics.values():
            if cache.get(key) is None:
                cache.set(key, 0, timeout=86400)  # 24 hours timeout

    def get_cached_tokens(self, user):
        """Get cached tokens or generate new ones"""
        cache_key = f'user_tokens_{user.id}'
        tokens = cache.get(cache_key)
        
        if not tokens:
            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
            cache.set(cache_key, tokens, timeout=300)
        
        return tokens

    def check_login_attempts(self, request):
        """Check and manage login attempts"""
        key = f"login_attempts_{request.META.get('REMOTE_ADDR')}"
        attempts = cache.get(key, 0)
        
        if attempts >= 5:  # Max 5 attempts
            logger.warning(f"Too many login attempts from IP: {request.META.get('REMOTE_ADDR')}")
            return False
            
        cache.set(key, attempts + 1, timeout=300)  # 5 minutes timeout
        return True

    @transaction.atomic
    def post(self, request):
        try:
            # Initialize cache metrics
            self.initialize_cache_metrics()

            # Check rate limiting
            if not self.check_login_attempts(request):
                return Response({
                    "error": "Too many failed attempts. Please try again later.",
                    "detail": "Rate limit exceeded"
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            serializer = LoginSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid login attempt for user: {request.data.get('usernameOrEmail')}")
                return Response({
                    "error": "Invalid credentials",
                    "detail": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.validated_data['user']
            tokens = self.get_cached_tokens(user)

            # Cache user data
            cache_key = f'user_data_{user.id}'
            user_data = {
                "username": user.username,
                "email": user.email,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "role": user.profile.role if hasattr(user, 'profile') else None
            }
            cache.set(cache_key, user_data, timeout=3600)

            # Update metrics safely
            try:
                cache.incr('active_sessions')
                AuthenticationMonitor.log_auth_metrics()
            except Exception as e:
                logger.warning(f"Failed to update metrics: {str(e)}")

            # Update user's last login
            user.update_last_login()
            user.reset_failed_attempts()

            logger.info(f"Successful login for user: {user.username}")
            return Response({
                "message": "Login successful",
                "user": user_data,
                "tokens": tokens
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Update failed attempts metric safely
            try:
                cache.incr('failed_attempts')
            except Exception as cache_error:
                logger.warning(f"Failed to update failed attempts metric: {str(cache_error)}")

            logger.error(f"Login failed with error: {str(e)}", exc_info=True)
            return Response({
                "error": "Login failed",
                "detail": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get refresh token
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({
                    "error": "Refresh token is required",
                    "detail": "Please provide the refresh token in the request body"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the token
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError as e:
                return Response({
                    "error": "Invalid token",
                    "detail": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

            # Clear user's cached data
            cache_key = f'user_data_{request.user.id}'
            cache.delete(cache_key)

            return Response({
                "message": "Logout successful",
                "detail": "User has been logged out and token has been blacklisted"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": "Logout failed",
                "detail": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['newPassword'])
            request.user.save()
            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

User = get_user_model()


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = PasswordResetRequestSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    logger.warning(f"Password reset attempted for non-existent email: {email}")
                    return Response({
                        "error": "Email not found",
                        "message": "No user is registered with this email address."
                    }, status=status.HTTP_404_NOT_FOUND)

                # Generate password reset token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Create reset link - use frontend URL from settings
                reset_url = settings.FRONTEND_URL + f"/reset-password/{uid}/{token}"
                
                # Email content
                context = {
                    'user': user,
                    'reset_url': reset_url,
                    'valid_hours': settings.PASSWORD_RESET_TIMEOUT // 3600,  # Convert seconds to hours
                    'site_name': settings.SITE_NAME
                }
                
                # Render email templates
                try:
                    html_content = render_to_string('authentication/password_reset_email.html', context)
                    text_content = render_to_string('authentication/password_reset_email.txt', context)
                except Exception as template_error:
                    logger.error(f"Template rendering error: {str(template_error)}")
                    raise ValidationError("Error generating email content")
                
                # Send email
                try:
                    msg = EmailMultiAlternatives(
                        subject='Password Reset Request',
                        body=text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[email]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send(fail_silently=False)
                    
                    logger.info(f"Password reset email sent successfully to {email}")
                    
                    # Cache the token for validation
                    cache_key = f'password_reset_{uid}'
                    cache.set(cache_key, token, timeout=settings.PASSWORD_RESET_TIMEOUT)
                    
                    return Response({
                        "message": "Password reset email sent",
                        "detail": f"Password reset instructions have been sent to {email}"
                    }, status=status.HTTP_200_OK)
                    
                except Exception as email_error:
                    logger.error(f"Email sending failed: {str(email_error)}")
                    raise ValidationError("Failed to send password reset email")
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except ValidationError as e:
            return Response({
                "error": "Password reset failed",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return Response({
                "error": "Password reset failed",
                "message": "An unexpected error occurred"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data={
            **request.data,
            'uidb64': uidb64,
            'token': token
        })
        if serializer.is_valid():
            # Add your password reset confirmation logic here
            return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, request):
        cache_key = f'user_data_{request.user.id}'
        user_data = cache.get(cache_key)
        
        if not user_data:
            user_data = {
                "username": request.user.username,
                "email": request.user.email
            }
            cache.set(cache_key, user_data, timeout=3600)
        
        return Response(user_data)