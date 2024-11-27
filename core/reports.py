from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from django.core.files.base import ContentFile
import csv
import io
import json

class ReportGenerator:
    """Base class for generating reports"""
    
    @staticmethod
    def generate_csv(data, headers):
        """Generate CSV report"""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
        return ContentFile(output.getvalue().encode('utf-8'))

    @staticmethod
    def generate_json(data):
        """Generate JSON report"""
        return ContentFile(json.dumps(data, default=str).encode('utf-8'))

class ReportScheduler:
    """Class for scheduling report generation"""
    
    @staticmethod
    def schedule_report(report_type, parameters, schedule_time):
        """Schedule a report for generation"""
        from apps.reports.models import Report
        
        report = Report.objects.create(
            report_type=report_type,
            parameters=parameters,
            scheduled_time=schedule_time,
            status='SCHEDULED'
        )
        return report

    @staticmethod
    def process_scheduled_reports():
        """Process all scheduled reports that are due"""
        from apps.reports.models import Report
        
        now = timezone.now()
        scheduled_reports = Report.objects.filter(
            status='SCHEDULED',
            scheduled_time__lte=now
        )
        
        for report in scheduled_reports:
            try:
                # Generate report
                report.generate()
                report.status = 'COMPLETED'
            except Exception as e:
                report.status = 'FAILED'
                report.error_message = str(e)
            report.save() 