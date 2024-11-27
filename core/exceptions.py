from rest_framework.exceptions import APIException
from rest_framework import status
from .constants import ERROR_MESSAGES
import logging

logger = logging.getLogger(__name__)

class BaseAPIException(Exception):
    """
    Base exception class for custom API exceptions.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An error occurred.'
    default_code = 'error'

    def __init__(self, message, code=None, extra=None):
        super().__init__(message)
        self.code = code
        self.extra = extra or {}
        logger.error(f"API Exception: {message}", extra={
            'code': code,
            'extra': extra
        })

class ValidationError(BaseAPIException):
    """
    Exception for validation errors.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = ERROR_MESSAGES['INVALID_REQUEST']
    default_code = 'validation_error'

class AuthenticationError(BaseAPIException):
    """
    Exception for authentication errors.
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = ERROR_MESSAGES['INVALID_CREDENTIALS']
    default_code = 'authentication_error'

class PermissionDenied(BaseAPIException):
    """
    Exception for permission errors.
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = ERROR_MESSAGES['PERMISSION_DENIED']
    default_code = 'permission_denied'

class ObjectNotFound(BaseAPIException):
    """
    Exception for not found errors.
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = ERROR_MESSAGES['OBJECT_NOT_FOUND']
    default_code = 'not_found'

class InvalidOperation(BaseAPIException):
    """
    Exception for invalid operations.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'This operation is not valid.'
    default_code = 'invalid_operation'

class DuplicateEntry(BaseAPIException):
    """
    Exception for duplicate entries.
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'This entry already exists.'
    default_code = 'duplicate_entry'

class ServiceUnavailable(BaseAPIException):
    """
    Exception for service unavailability.
    """
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable.'
    default_code = 'service_unavailable'

class DatabaseError(BaseAPIException):
    """
    Exception for database errors.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A database error occurred.'
    default_code = 'database_error'

class FileUploadError(BaseAPIException):
    """
    Exception for file upload errors.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Error uploading file.'
    default_code = 'file_upload_error' 