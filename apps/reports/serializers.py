from rest_framework import serializers
from .models import ReportTemplate, Report

class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(
        source='template.name',
        read_only=True
    )
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ('generated_file',) 