from django.contrib import admin
from .models import Asset, AssetMaintenance, AssetAssignment, AssetRequest

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('asset_id', 'name', 'category', 'department', 'asset_status', 'assigned_to')
    list_filter = ('asset_status', 'category', 'department')
    search_fields = ('asset_id', 'name', 'description')
    readonly_fields = ('asset_id', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('asset_id', 'name', 'description', 'category')
        }),
        ('Assignment', {
            'fields': ('department', 'assigned_to', 'asset_status')
        }),
        ('Financial', {
            'fields': ('purchase_price', 'purchase_date', 'warranty_expiry')
        }),
        ('Tracking', {
            'fields': ('qr_code', 'created_at', 'updated_at')
        }),
    )

@admin.register(AssetMaintenance)
class AssetMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('maintenance_id', 'asset', 'maintenance_date', 'maintenance_type', 'performed_by')
    list_filter = ('maintenance_date', 'maintenance_type')
    search_fields = ('maintenance_id', 'asset__name', 'asset__asset_id', 'description')
    readonly_fields = ('maintenance_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('maintenance_id', 'asset', 'maintenance_type')
        }),
        ('Maintenance Details', {
            'fields': ('maintenance_date', 'description', 'cost', 'performed_by')
        }),
        ('Follow-up', {
            'fields': ('next_maintenance_date', 'attachments')
        }),
        ('Tracking', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(AssetAssignment)
class AssetAssignmentAdmin(admin.ModelAdmin):
    list_display = ('asset', 'assigned_to', 'assigned_date', 'return_date')
    list_filter = ('assigned_date', 'return_date')
    search_fields = ('asset__name', 'assigned_to__user__username')
    readonly_fields = ('created_at',)

@admin.register(AssetRequest)
class AssetRequestAdmin(admin.ModelAdmin):
    list_display = ('asset', 'requested_by', 'request_date', 'status')
    list_filter = ('status', 'request_date')
    search_fields = ('asset__name', 'requested_by__user__username')
    readonly_fields = ('created_at',)
