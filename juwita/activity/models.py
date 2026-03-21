from django.db import models

class Log(models.Model):
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)  # optional extra data

    def __str__(self):
        return f"{self.action} at {self.timestamp}"
    
    