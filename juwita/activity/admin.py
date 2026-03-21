from django.contrib import admin
from .models import Log

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('action', 'timestamp')       
    list_filter = ('timestamp',)                 
    search_fields = ('action',)