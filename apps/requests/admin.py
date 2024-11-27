from django.contrib import admin
from .models import RequestType, AssetRequest, RequestApproval

@admin.register(RequestType)
class RequestTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'requires_approval', 'approval_levels')
    list_filter = ('requires_approval', 'created_at')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('code', 'created_at', 'updated_at')

@admin.register(AssetRequest)
class AssetRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'title', 'requester', 'request_type', 'status', 'priority')
    list_filter = ('status', 'priority', 'request_type', 'created_at')
    search_fields = ('request_id', 'title', 'description', 'requester__username')
    readonly_fields = ('request_id', 'created_at', 'updated_at', 'completion_date')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('request_id', 'title', 'description', 'request_type')
        }),
        ('Request Details', {
            'fields': ('requester', 'asset', 'priority', 'status')
        }),
        ('Dates', {
            'fields': ('desired_date', 'completion_date', 'created_at', 'updated_at')
        }),
        ('Attachments', {
            'fields': ('attachments',)
        }),
    )

@admin.register(RequestApproval)
class RequestApprovalAdmin(admin.ModelAdmin):
    list_display = ('request', 'approver', 'approval_level', 'status', 'approval_date')
    list_filter = ('status', 'approval_level', 'approval_date')
    search_fields = ('request__request_id', 'approver__username', 'comments')
    readonly_fields = ('approval_date', 'created_at', 'updated_at')
