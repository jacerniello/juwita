from django.contrib import admin
from .models import Log
from zoneinfo import ZoneInfo
from django.utils.timezone import is_aware, make_aware
from datetime import timezone  # for UTC

EASTERN_TZ = ZoneInfo("America/New_York")

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('action', 'timestamp_eastern', 'metadata')
    list_filter = ('timestamp',)
    search_fields = ('action',)

    def timestamp_eastern(self, obj):
        timestamp = obj.timestamp

        # Make naive datetime aware as UTC
        if not is_aware(timestamp):
            timestamp = make_aware(timestamp, timezone.utc)

        # Convert to Eastern Time
        eastern_time = timestamp.astimezone(EASTERN_TZ)
        return eastern_time.strftime('%Y-%m-%d %H:%M:%S %Z')

    # sort by original UTC
    timestamp_eastern.admin_order_field = 'timestamp'  
    timestamp_eastern.short_description = 'Timestamp (Eastern)'