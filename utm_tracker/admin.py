from django.contrib import admin

from .models import LeadSource


class LeadSourceAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)
    list_display = ("user", "medium", "source", "campaign", "timestamp")
    search_fields = ("user__first_name", "user__last_name", "term", "content")
    list_filter = ("medium", "source", "timestamp")
    readonly_fields = ("created_at", "timestamp")


admin.site.register(LeadSource, LeadSourceAdmin)
