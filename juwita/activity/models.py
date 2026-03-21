from django.db import models
from django.utils import timezone
from datetime import timedelta


class Log(models.Model):
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.action} at {self.timestamp}"


class Meeting(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    last_ping = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, default='')

    PING_TIMEOUT = 30  # seconds - meeting ends after this much silence

    @property
    def is_active(self):
        if self.end_time:
            return False
        return (timezone.now() - self.last_ping).total_seconds() < self.PING_TIMEOUT

    @property
    def duration(self):
        end = self.end_time or timezone.now()
        return end - self.start_time

    @classmethod
    def get_or_create_active(cls):
        """Get active meeting or create new one. Closes stale meetings."""
        now = timezone.now()
        timeout = timedelta(seconds=cls.PING_TIMEOUT)

        # Find meeting that hasn't ended and last ping is recent
        active = cls.objects.filter(end_time__isnull=True).order_by('-last_ping').first()

        if active:
            if now - active.last_ping > timeout:
                # Close stale meeting
                active.end_time = active.last_ping
                active.save()
                # Create new meeting
                return cls.objects.create()
            else:
                # Update last ping
                active.last_ping = now
                active.save()
                return active
        else:
            # No active meeting, create one
            return cls.objects.create()

    def __str__(self):
        status = "active" if self.is_active else "ended"
        return f"Meeting {self.id} ({status}) - {self.start_time}"


class MeetingPhoto(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='meeting_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for Meeting {self.meeting_id}"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#6b7280')  # hex color
    meetings = models.ManyToManyField(Meeting, related_name='tags', blank=True)

    def __str__(self):
        return self.name
