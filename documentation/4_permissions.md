# Permissions System Documentation

## Role-Based Access Control (RBAC)

### User Roles

1. **Admin (ADMIN)**
   - Full system access
   - Can manage users and roles
   - Can approve/reject any request
   - Can manage all assets
   - Can generate all reports
   - Can configure system settings

2. **Manager (MANAGER)**
   - Department-level access
   - Can manage department users
   - Can approve department requests
   - Can manage department assets
   - Can view department reports
   - Can assign assets within department

3. **User (USER)**
   - Basic access level
   - Can view assigned assets
   - Can create requests
   - Can view own profile
   - Can view basic reports
   - Can update own information

### Permission Classes

1. **IsAdmin**
   ```python
   class IsAdmin(permissions.BasePermission):
       def has_permission(self, request, view):
           return bool(request.user and 
                      request.user.is_authenticated and 
                      request.user.profile.role == ROLE_ADMIN)
   ```

2. **IsManager**
   ```python
   class IsManager(permissions.BasePermission):
       def has_permission(self, request, view):
           return bool(request.user and 
                      request.user.is_authenticated and 
                      request.user.profile.role == ROLE_MANAGER)
   ```

3. **IsOwnerOrAdmin**
   ```python
   class IsOwnerOrAdmin(permissions.BasePermission):
       def has_object_permission(self, request, view, obj):
           if request.user.profile.role == ROLE_ADMIN:
               return True
           return obj.created_by == request.user
   ```

4. **CanApproveRequests**
   ```python
   class CanApproveRequests(permissions.BasePermission):
       def has_permission(self, request, view):
           return bool(request.user and 
                      request.user.is_authenticated and 
                      request.user.profile.role in [ROLE_ADMIN, ROLE_MANAGER])
   ```

### Permission Matrix

#### User Management
| Action | Admin | Manager | User |
|--------|--------|----------|------|
| View Users | All Users | Department Users | Self Only |
| Create User | ✓ | × | × |
| Update User | All Users | Department Users | Self Only |
| Delete User | ✓ | × | × |
| Change Roles | ✓ | × | × |

#### Asset Management
| Action | Admin | Manager | User |
|--------|--------|----------|------|
| View Assets | All Assets | Department Assets | Assigned Assets |
| Create Asset | ✓ | × | × |
| Update Asset | All Assets | Department Assets | × |
| Delete Asset | ✓ | × | × |
| Assign Asset | All Assets | Department Assets | × |

#### Request Management
| Action | Admin | Manager | User |
|--------|--------|----------|------|
| View Requests | All Requests | Department Requests | Own Requests |
| Create Request | ✓ | ✓ | ✓ |
| Approve Request | All Requests | Department Requests | × |
| Cancel Request | All Requests | Department Requests | Own Requests |

#### Report Management
| Action | Admin | Manager | User |
|--------|--------|----------|------|
| View Reports | All Reports | Department Reports | Basic Reports |
| Generate Reports | ✓ | Department Only | × |
| Schedule Reports | ✓ | × | × |
| Export Reports | All Formats | Limited Formats | Basic Formats |

### Implementation Details

1. **View-Level Permissions**
   ```python
   class AssetViewSet(viewsets.ModelViewSet):
       permission_classes = [IsAuthenticated, IsAdmin|IsManager]
       
       def get_queryset(self):
           user = self.request.user
           if user.profile.is_admin:
               return Asset.objects.all()
           elif user.profile.is_manager:
               return Asset.objects.filter(department=user.profile.department)
           return Asset.objects.filter(assigned_to=user)
   ```

2. **Model-Level Permissions**
   ```python
   class Asset(AuditableModel):
       def can_user_edit(self, user):
           if user.profile.is_admin:
               return True
           if user.profile.is_manager:
               return self.department == user.profile.department
           return False
   ```

3. **Action-Level Permissions**
   ```python
   @action(detail=True, methods=['post'])
   def approve(self, request, pk=None):
       if not request.user.profile.can_approve_requests:
           return Response(status=status.HTTP_403_FORBIDDEN)
   ```

### Permission Inheritance

1. **Department-Based**
   - Managers inherit permissions for their department
   - Department permissions cascade to sub-departments
   - Asset permissions follow department hierarchy

2. **Role-Based**
   - Admin inherits all permissions
   - Manager inherits department-level permissions
   - User has basic permissions

3. **Object-Level**
   - Creator has full access to their objects
   - Department managers have access to department objects
   - Users have access to assigned objects

### Security Considerations

1. **Authentication Required**
   - All endpoints require authentication
   - JWT tokens used for API access
   - Token refresh mechanism implemented

2. **Permission Checks**
   - Multiple levels of permission checks
   - Both class-based and method-based checks
   - Object-level permission validation

3. **Audit Trail**
   - All permission changes are logged
   - Failed permission attempts are recorded
   - Regular permission audits

### Best Practices

1. **Permission Assignment**
   - Follow principle of least privilege
   - Regular permission reviews
   - Document permission changes
   - Audit permission usage

2. **Implementation**
   - Use built-in Django permissions
   - Implement custom permission classes
   - Combine permissions using logical operators
   - Cache permission checks when appropriate

3. **Maintenance**
   - Regular permission cleanup
   - Remove unused permissions
   - Update permission documentation
   - Monitor permission usage patterns 