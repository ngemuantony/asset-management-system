from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'parent', 'asset_count')
    list_filter = ('created_at', 'status')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('code', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Hierarchy', {
            'fields': ('parent',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Tracking', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def asset_count(self, obj):
        return obj.asset_count
    asset_count.short_description = 'Assets'
