from rest_framework import permissions

class IsDepartmentAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admins to manage departments.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.profile.role == 'ADMIN'

class IsDepartmentManager(permissions.BasePermission):
    """
    Custom permission to allow department managers to view their department.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.profile.role == 'ADMIN':
            return True
        return request.user.profile.department == obj 