from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Log, Meeting
import json


@csrf_exempt
def log_action(request):
    if request.method == "POST":
        data = json.loads(request.body)
        action = data.get("action", "button_clicked")
        metadata = {
            "ip": request.META.get("REMOTE_ADDR"),
            "user_agent": request.META.get("HTTP_USER_AGENT")
        }
        log = Log.objects.create(action=action, metadata=metadata)
        return JsonResponse({"success": True, "log_id": log.id})
    return JsonResponse({"error": "Invalid request"}, status=400)


def ping(request):
    """ESP device pings this endpoint. Manages meeting state automatically."""
    # Log the ping
    metadata = {
        "ip": request.META.get("REMOTE_ADDR"),
        "user_agent": request.META.get("HTTP_USER_AGENT")
    }
    log = Log.objects.create(action="ping", metadata=metadata)

    # Get or create active meeting
    meeting = Meeting.get_or_create_active()

    return JsonResponse({
        "success": True,
        "ping_id": log.id,
        "timestamp": log.timestamp.isoformat(),
        "meeting_id": meeting.id,
        "meeting_active": meeting.is_active
    })


def meetings(request):
    """Return all meetings with their status."""
    now = timezone.now()

    # Close any stale meetings
    stale_meetings = Meeting.objects.filter(
        end_time__isnull=True
    ).exclude(
        last_ping__gte=now - timezone.timedelta(seconds=Meeting.PING_TIMEOUT)
    )
    for m in stale_meetings:
        m.end_time = m.last_ping
        m.save()

    # Get active meeting
    active = Meeting.objects.filter(end_time__isnull=True).first()

    # Get completed meetings
    completed = Meeting.objects.filter(end_time__isnull=False).order_by('-start_time')[:20]

    result = {
        "active_meeting": {
            "id": active.id,
            "start": active.start_time.isoformat(),
            "duration_minutes": active.duration.total_seconds() / 60,
            "last_ping": active.last_ping.isoformat()
        } if active and active.is_active else None,
        "meetings": [
            {
                "id": m.id,
                "start": m.start_time.isoformat(),
                "end": m.end_time.isoformat(),
                "duration_minutes": m.duration.total_seconds() / 60
            }
            for m in completed
        ]
    }

    return JsonResponse(result)


@csrf_exempt
def delete_meeting(request, meeting_id):
    """Delete a meeting by ID."""
    if request.method == "DELETE":
        try:
            meeting = Meeting.objects.get(id=meeting_id)
            meeting.delete()
            return JsonResponse({"success": True})
        except Meeting.DoesNotExist:
            return JsonResponse({"error": "Meeting not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)


def index(request):
    return render(request, 'activity/index.html')
