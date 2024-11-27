from rest_framework import permissions
from core.constants import ROLE_ADMIN, ROLE_MANAGER

print("Loading core permissions")

class IsAdmin(permissions.BasePermission):
    """
    Permission check for admin users
    """
    def has_permission(self, request, view):
        return bool(request.user and 
                   request.user.is_authenticated and 
                   request.user.profile.role == ROLE_ADMIN)

# Alias for backwards compatibility
IsAdminUser = IsAdmin

class IsManager(permissions.BasePermission):
    """
    Permission check for manager users
    """
    def has_permission(self, request, view):
        return bool(request.user and 
                   request.user.is_authenticated and 
                   request.user.profile.role == ROLE_MANAGER)

# Alias for backwards compatibility
IsManagerUser = IsManager

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object or admins to edit it
    """
    def has_object_permission(self, request, view, obj):
        if request.user.profile.role == ROLE_ADMIN:
            return True
        return obj.created_by == request.user 

class CanApproveRequests(permissions.BasePermission):
    """
    Permission check for users who can approve requests
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.profile.role in [ROLE_ADMIN, ROLE_MANAGER]
        )

class IsRequesterOrApprover(permissions.BasePermission):
    """
    Object-level permission to only allow requesters or approvers to view/edit
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Allow if user is the requester
        if obj.requester == user:
            return True
            
        # Allow if user is an approver for this request
        if obj.approvals.filter(approver=user).exists():
            return True
            
        # Allow if user is admin
        if user.profile.role == ROLE_ADMIN:
            return True
            
        return False 