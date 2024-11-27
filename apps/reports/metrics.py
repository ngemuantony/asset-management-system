from django.db.models import Count, Avg, Sum, F, ExpressionWrapper, DurationField, Q
from django.utils import timezone
from datetime import timedelta
from apps.assets.models import Asset, AssetAssignment
from apps.requests.models import AssetRequest
from django.db.models.functions import TruncMonth, TruncWeek, ExtractYear

class AssetMetrics:
    """
    Class for calculating various asset-related metrics
    """
    
    @staticmethod
    def get_most_used_assets(limit=10):
        """Get assets with the most assignments/usage"""
        return Asset.objects.annotate(
            assignment_count=Count('asset_assignments'),
            total_usage_days=Sum(
                ExpressionWrapper(
                    F('asset_assignments__end_date') - F('asset_assignments__start_date'),
                    output_field=DurationField()
                )
            )
        ).order_by('-assignment_count')[:limit]

    @staticmethod
    def get_asset_utilization_rate():
        """Calculate asset utilization rate"""
        total_assets = Asset.objects.count()
        assigned_assets = Asset.objects.filter(
            asset_status='ASSIGNED'
        ).count()
        
        return {
            'total_assets': total_assets,
            'assigned_assets': assigned_assets,
            'utilization_rate': (assigned_assets / total_assets * 100) if total_assets > 0 else 0
        }

    @staticmethod
    def get_asset_request_metrics():
        """Get metrics about asset requests"""
        total_requests = AssetRequest.objects.count()
        pending_requests = AssetRequest.objects.filter(status='PENDING').count()
        approved_requests = AssetRequest.objects.filter(status='APPROVED').count()
        rejected_requests = AssetRequest.objects.filter(status='REJECTED').count()
        
        return {
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'approved_requests': approved_requests,
            'rejected_requests': rejected_requests,
            'approval_rate': (approved_requests / total_requests * 100) if total_requests > 0 else 0
        }

    @staticmethod
    def get_asset_maintenance_metrics():
        """Get metrics about asset maintenance"""
        return Asset.objects.filter(
            asset_status='MAINTENANCE'
        ).aggregate(
            total_in_maintenance=Count('id'),
            avg_maintenance_cost=Avg('maintenance_records__cost'),
            total_maintenance_cost=Sum('maintenance_records__cost')
        )

    @staticmethod
    def get_asset_lifecycle_metrics():
        """Get metrics about asset lifecycle"""
        current_date = timezone.now()
        return Asset.objects.aggregate(
            avg_age=Avg(current_date - F('purchase_date')),
            total_value=Sum('purchase_price'),
            depreciated_value=Sum('current_value')
        )

    @staticmethod
    def get_department_usage_metrics():
        """Get metrics about asset usage by department"""
        return Asset.objects.values(
            'department__name'
        ).annotate(
            asset_count=Count('id'),
            total_value=Sum('purchase_price'),
            utilization_rate=Count('id', filter=Q(asset_status='ASSIGNED')) * 100.0 / Count('id')
        ).order_by('-asset_count')

    @staticmethod
    def get_trending_metrics(days=30):
        """Get trending metrics over time"""
        start_date = timezone.now() - timedelta(days=days)
        
        # Asset requests over time
        requests_trend = AssetRequest.objects.filter(
            created_at__gte=start_date
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            count=Count('id')
        ).order_by('week')
        
        # Asset assignments over time
        assignments_trend = AssetAssignment.objects.filter(
            start_date__gte=start_date
        ).annotate(
            week=TruncWeek('start_date')
        ).values('week').annotate(
            count=Count('id')
        ).order_by('week')
        
        return {
            'requests_trend': list(requests_trend),
            'assignments_trend': list(assignments_trend)
        }

    @staticmethod
    def get_category_metrics():
        """Get metrics by asset category"""
        return Asset.objects.values(
            'category__name'
        ).annotate(
            asset_count=Count('id'),
            total_value=Sum('purchase_price'),
            maintenance_count=Count('maintenance_records'),
            avg_utilization=Avg(
                Case(
                    When(asset_status='ASSIGNED', then=1),
                    default=0,
                    output_field=FloatField(),
                )
            ) * 100
        ).order_by('-asset_count') 