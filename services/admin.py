from django.contrib import admin
from .models import District, Location, Service, Vendor, Lead
from datetime import datetime, timedelta

# Inline for Locations under District
class LocationInline(admin.TabularInline):
    model = Location
    extra = 0

# Custom filter for recent leads
class RecentLeadFilter(admin.SimpleListFilter):
    title = 'Recent Leads'
    parameter_name = 'recent'

    def lookups(self, request, model_admin):
        return [('7days', 'Last 7 Days')]

    def queryset(self, request, queryset):
        if self.value() == '7days':
            week_ago = datetime.now() - timedelta(days=7)
            return queryset.filter(created_at__gte=week_ago)

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("district_name", "slug", "created_at", "is_active")
    search_fields = ("district_name",)
    prepopulated_fields = {"slug": ("district_name",)}
    inlines = [LocationInline]
    list_editable = ("is_active",)
    list_per_page = 25

    def get_readonly_fields(self, request, obj=None):
        return ("slug",) if obj else ()

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("location_name", "district", "slug", "created_at", "is_active")
    list_filter = ("district",)
    search_fields = ("location_name",)
    prepopulated_fields = {"slug": ("location_name",)}
    list_editable = ("is_active",)
    list_per_page = 25

    def get_readonly_fields(self, request, obj=None):
        return ("slug",) if obj else ()

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("service_name", "slug", "created_at", "is_active")
    search_fields = ("service_name",)
    prepopulated_fields = {"slug": ("service_name",)}
    list_editable = ("is_active",)
    list_per_page = 25

    def get_readonly_fields(self, request, obj=None):
        return ("slug",) if obj else ()

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("vendor_name", "location", "created_at", "is_active")
    list_filter = ("location",)
    search_fields = ("vendor_name",)
    list_editable = ("is_active",)
    list_per_page = 25
    actions = ["deactivate_selected"]

    @admin.action(description="Mark selected vendors as inactive")
    def deactivate_selected(self, request, queryset):
        queryset.update(is_active=False)

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("lead_id", "lead_name", "phone_number", "district", "location", "service", "created_at", "is_active")
    list_filter = ("district", "location", "service", RecentLeadFilter)
    search_fields = ("lead_name", "phone_number")
    readonly_fields = ("lead_id", "created_at", "updated_at")
    list_editable = ("is_active",)
    list_per_page = 25
    actions = ["deactivate_selected"]

    fieldsets = (
        ("Customer Info", {
            "fields": ("lead_name", "phone_number")
        }),
        ("Request Details", {
            "fields": ("district", "location", "service")
        }),
        ("System Info", {
            "fields": ("lead_id", "created_at", "updated_at", "is_active", "created_by")
        }),
    )

    @admin.action(description="Mark selected leads as inactive")
    def deactivate_selected(self, request, queryset):
        queryset.update(is_active=False)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_active=True)
