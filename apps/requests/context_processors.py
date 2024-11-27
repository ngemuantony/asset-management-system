def pending_requests(request):
    """Add pending requests count to context"""
    if request.user.is_authenticated:
        return {
            'pending_requests_count': request.user.asset_requests.filter(
                status='PENDING'
            ).count()
        }
    return {'pending_requests_count': 0} 