from django.core.cache import cache
from django.utils import timezone
from apps.departments.models import Department

def cache_department_tree(departments):
    """Optimized department tree caching"""
    department_tree = {}
    # Prefetch related data to avoid N+1 queries
    departments = departments.prefetch_related('sub_departments')
    
    for dept in departments:
        cache_key = f'department_tree_{dept.id}'
        if cache.get(cache_key):
            continue  # Skip if already cached
            
        department_tree[dept.id] = {
            'name': dept.name,
            'parent': dept.parent_id,
            'children': list(dept.sub_departments.values_list('id', flat=True)),
            'member_count': dept.member_count,
            'last_updated': timezone.now().isoformat()
        }
        cache.set(cache_key, department_tree[dept.id], timeout=3600)
    
    return department_tree 

def invalidate_department_cache(department_id):
    """
    Bug: Cache invalidation not cascading to related objects
    Solution: Implement proper cache invalidation
    """
    keys_to_delete = [
        f'department_tree_{department_id}',
        f'department_stats_{department_id}',
        f'department_users_{department_id}',
        f'department_assets_{department_id}'
    ]
    
    # Get parent and child departments
    department = Department.objects.get(id=department_id)
    if department.parent:
        keys_to_delete.append(f'department_tree_{department.parent.id}')
    
    for child in department.sub_departments.all():
        keys_to_delete.append(f'department_tree_{child.id}')
    
    cache.delete_many(keys_to_delete) 