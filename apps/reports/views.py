from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import ReportTemplate, Report
from .serializers import ReportTemplateSerializer, ReportSerializer
from core.permissions import IsAdminUser, IsManagerUser
from core.utils import generate_pdf, generate_excel
from apps.assets.models import Asset, AssetMaintenance, AssetAssignment
from apps.users.models import UserActivityLog
from django.db.models.functions import TruncDate
from .metrics import AssetMetrics
from django.db.models import ExpressionWrapper, F, DurationField
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet for managing reports"""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, IsAdminUser|IsManagerUser]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard statistics"""
        # Asset statistics
        total_assets = Asset.objects.count()
        available_assets = Asset.objects.filter(
            asset_status='AVAILABLE'
        ).count()
        assigned_assets = Asset.objects.filter(
            asset_status='ASSIGNED'
        ).count()
        maintenance_assets = Asset.objects.filter(
            asset_status='MAINTENANCE'
        ).count()
        
        # Maintenance statistics
        maintenance_this_month = AssetMaintenance.objects.filter(
            maintenance_date__month=timezone.now().month
        ).count()
        
        # Assignment statistics
        assignments_this_month = AssetAssignment.objects.filter(
            assigned_date__month=timezone.now().month
        ).count()
        
        return Response({
            'assets': {
                'total': total_assets,
                'available': available_assets,
                'assigned': assigned_assets,
                'maintenance': maintenance_assets,
            },
            'maintenance': {
                'this_month': maintenance_this_month,
            },
            'assignments': {
                'this_month': assignments_this_month,
            }
        })
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new report"""
        template_id = request.data.get('template_id')
        report_format = request.data.get('format', 'PDF')
        parameters = request.data.get('parameters', {})
        
        try:
            template = ReportTemplate.objects.get(id=template_id)
            
            # Generate report based on template type
            if template.template_type == 'ASSET':
                data = self._generate_asset_report(parameters)
            elif template.template_type == 'MAINTENANCE':
                data = self._generate_maintenance_report(parameters)
            elif template.template_type == 'ASSIGNMENT':
                data = self._generate_assignment_report(parameters)
            else:
                return Response(
                    {"error": "Invalid template type"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate file based on format
            if report_format == 'PDF':
                report_file = generate_pdf(template.template_file, data)
            elif report_format in ['EXCEL', 'CSV']:
                report_file = generate_excel(data, report_format)
            else:
                return Response(
                    {"error": "Invalid format"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create report record
            report = Report.objects.create(
                template=template,
                format=report_format,
                parameters=parameters,
                generated_file=report_file
            )
            
            return Response(
                ReportSerializer(report).data,
                status=status.HTTP_201_CREATED
            )
            
        except ReportTemplate.DoesNotExist:
            return Response(
                {"error": "Template not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_asset_report(self, parameters):
        """Generate asset report data"""
        queryset = Asset.objects.all()
        
        # Apply filters from parameters
        if parameters.get('status'):
            queryset = queryset.filter(asset_status=parameters['status'])
        if parameters.get('category'):
            queryset = queryset.filter(category_id=parameters['category'])
        if parameters.get('department'):
            queryset = queryset.filter(department_id=parameters['department'])
            
        return {
            'assets': queryset,
            'total_count': queryset.count(),
            'total_value': queryset.aggregate(
                total=Sum('purchase_price')
            )['total']
        }
    
    @action(detail=False, methods=['get'])
    def user_activity(self, request):
        """Generate user activity report"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = UserActivityLog.objects.all()
        
        if start_date and end_date:
            queryset = queryset.filter(
                timestamp__range=[start_date, end_date]
            )
            
        report_data = {
            'daily_activity': queryset\
                .annotate(date=TruncDate('timestamp'))\
                .values('date')\
                .annotate(count=Count('id'))\
                .order_by('date'),
                
            'activity_by_type': queryset\
                .values('action')\
                .annotate(count=Count('id'))\
                .order_by('-count'),
                
            'user_statistics': queryset\
                .values('user__username')\
                .annotate(
                    total_actions=Count('id'),
                    unique_ips=Count('ip_address', distinct=True)
                )\
                .order_by('-total_actions'),
                
            'ip_addresses': queryset\
                .values('ip_address')\
                .annotate(count=Count('id'))\
                .order_by('-count')
        }
        
        return Response(report_data)

class MetricsViewSet(viewsets.ViewSet):
    """
    ViewSet for accessing various system metrics and analytics.
    Provides endpoints for retrieving different types of metrics about assets, departments, and system usage.
    """
    permission_classes = [IsAuthenticated]
    basename = 'metrics'

    def get_view_name(self):
        return "System Metrics"

    def get_view_description(self, html=False):
        return "Endpoints for retrieving various system metrics and analytics data"

    @swagger_auto_schema(
        operation_description="Get comprehensive dashboard metrics",
        responses={
            200: openapi.Response(
                description="Dashboard metrics retrieved successfully",
                examples={
                    "application/json": {
                        "asset_overview": {
                            "total_assets": 100,
                            "assigned_assets": 75,
                            "utilization_rate": 75.0
                        },
                        "top_assets": ["Asset details..."],
                        "department_summary": ["Department metrics..."],
                        "maintenance_stats": {
                            "total_in_maintenance": 5,
                            "avg_maintenance_cost": 1000.00
                        },
                        "request_summary": {
                            "total_requests": 50,
                            "pending_requests": 10
                        }
                    }
                }
            )
        }
    )
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get comprehensive dashboard metrics"""
        try:
            metrics = {
                'asset_overview': AssetMetrics.get_asset_utilization_rate(),
                'top_assets': AssetMetrics.get_most_used_assets(limit=5),
                'department_summary': AssetMetrics.get_department_usage_metrics(),
                'maintenance_stats': AssetMetrics.get_asset_maintenance_metrics(),
                'request_summary': AssetMetrics.get_asset_request_metrics(),
                'lifecycle_stats': AssetMetrics.get_asset_lifecycle_metrics()
            }
            return Response(metrics)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Get detailed asset metrics",
        manual_parameters=[
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Number of most used assets to return",
                type=openapi.TYPE_INTEGER,
                default=10
            )
        ],
        responses={200: "Asset metrics retrieved successfully"}
    )
    @action(detail=False, methods=['get'])
    def asset_overview(self, request):
        """Get detailed asset metrics"""
        try:
            metrics = {
                'utilization': AssetMetrics.get_asset_utilization_rate(),
                'most_used': AssetMetrics.get_most_used_assets(
                    limit=int(request.query_params.get('limit', 10))
                ),
                'requests': AssetMetrics.get_asset_request_metrics(),
                'maintenance': AssetMetrics.get_asset_maintenance_metrics()
            }
            return Response(metrics)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Get department usage metrics",
        manual_parameters=[
            openapi.Parameter(
                'department_id',
                openapi.IN_QUERY,
                description="Filter metrics by department ID",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={200: "Department metrics retrieved successfully"}
    )
    @action(detail=False, methods=['get'])
    def department_metrics(self, request):
        """Get department usage metrics"""
        try:
            department_id = request.query_params.get('department_id')
            metrics = AssetMetrics.get_department_usage_metrics()
            if department_id:
                metrics = metrics.filter(department_id=department_id)
            return Response(list(metrics))
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Get trending metrics over time",
        manual_parameters=[
            openapi.Parameter(
                'days',
                openapi.IN_QUERY,
                description="Number of days to analyze",
                type=openapi.TYPE_INTEGER,
                default=30
            )
        ],
        responses={200: "Trending metrics retrieved successfully"}
    )
    @action(detail=False, methods=['get'])
    def trending_metrics(self, request):
        """Get trending metrics over time"""
        try:
            days = int(request.query_params.get('days', 30))
            metrics = AssetMetrics.get_trending_metrics(days=days)
            return Response(metrics)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Get category-specific metrics",
        responses={200: "Category metrics retrieved successfully"}
    )
    @action(detail=False, methods=['get'])
    def category_metrics(self, request):
        """Get category-specific metrics"""
        try:
            metrics = AssetMetrics.get_category_metrics()
            return Response(list(metrics))
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Get asset lifecycle metrics",
        responses={200: "Lifecycle metrics retrieved successfully"}
    )
    @action(detail=False, methods=['get'])
    def asset_lifecycle(self, request):
        """Get asset lifecycle metrics"""
        try:
            metrics = AssetMetrics.get_asset_lifecycle_metrics()
            return Response(metrics)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Get detailed maintenance analysis",
        manual_parameters=[
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                description="Start date for analysis (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True
            ),
            openapi.Parameter(
                'end_date',
                openapi.IN_QUERY,
                description="End date for analysis (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True
            )
        ],
        responses={200: "Maintenance analysis retrieved successfully"}
    )
    @action(detail=False, methods=['get'])
    def maintenance_analysis(self, request):
        """Get detailed maintenance analysis"""
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            metrics = Asset.objects.filter(
                maintenance_records__maintenance_date__range=[start_date, end_date]
            ).annotate(
                maintenance_count=Count('maintenance_records'),
                total_cost=Sum('maintenance_records__cost'),
                avg_cost=Avg('maintenance_records__cost'),
                downtime_days=Sum(
                    ExpressionWrapper(
                        F('maintenance_records__end_date') - F('maintenance_records__start_date'),
                        output_field=DurationField()
                    )
                )
            ).values(
                'id', 'name', 'maintenance_count', 
                'total_cost', 'avg_cost', 'downtime_days'
            )
            
            return Response(list(metrics))
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
