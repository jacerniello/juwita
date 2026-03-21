from django.contrib import admin
from .models import Log
from django.utils.timezone import localtime
import pytz


EASTERN_TZ = pytz.timezone('US/Eastern')

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('action', 'timestamp_local', 'metadata')
    list_filter = ('timestamp',)
    search_fields = ('action',)

    def timestamp_local(self, obj):
        # Convert UTC to your desired timezone
        local_time = obj.timestamp.astimezone(EASTERN_TZ)
        # If you prefer Eastern Time, use EASTERN_TZ
        return local_time.strftime('%Y-%m-%d %H:%M:%S %Z')

    timestamp_local.admin_order_field = 'timestamp'  # allows sorting
    timestamp_local.short_description = 'Timestamp (Pacific)'