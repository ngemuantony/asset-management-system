from django.contrib import admin
from .models import Report, ReportTemplate

@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'created_at', 'updated_at')
    list_filter = ('template_type', 'created_at')
    search_fields = ('name', 'template_type')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'template', 'generation_time', 'format', 'generated_by')
    list_filter = ('format', 'generation_time', 'scheduled')
    search_fields = ('name', 'template__name')
    readonly_fields = ('generation_time', 'generated_by')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'template', 'format')
        }),
        ('Generation Details', {
            'fields': ('generated_by', 'generation_time', 'scheduled')
        }),
        ('Content', {
            'fields': ('parameters', 'generated_file')
        }),
        ('Relations', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        })
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Only set generated_by on creation
            obj.generated_by = request.user
        super().save_model(request, obj, form, change)
