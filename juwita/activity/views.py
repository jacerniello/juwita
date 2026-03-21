from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from .models import Log
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
    """ESP device pings this endpoint every ~30 seconds"""
    metadata = {
        "ip": request.META.get("REMOTE_ADDR"),
        "user_agent": request.META.get("HTTP_USER_AGENT")
    }
    log = Log.objects.create(action="ping", metadata=metadata)
    return JsonResponse({"success": True, "ping_id": log.id, "timestamp": log.timestamp.isoformat()})


def meetings(request):
    """Aggregate pings into meetings. A meeting ends after 5 minutes of no pings."""
    gap_minutes = int(request.GET.get("gap", 5))
    gap = timedelta(minutes=gap_minutes)

    pings = Log.objects.filter(action="ping").order_by("timestamp")

    meetings_list = []
    current_meeting = None

    for ping in pings:
        if current_meeting is None:
            current_meeting = {"start": ping.timestamp, "end": ping.timestamp}
        elif ping.timestamp - current_meeting["end"] > gap:
            # Gap detected, save current meeting and start new one
            meetings_list.append(current_meeting)
            current_meeting = {"start": ping.timestamp, "end": ping.timestamp}
        else:
            # Extend current meeting
            current_meeting["end"] = ping.timestamp

    # Add the last meeting if exists
    if current_meeting:
        meetings_list.append(current_meeting)

    # Check if there's an active meeting (last ping within gap time)
    now = timezone.now()
    active_meeting = None
    if meetings_list and now - meetings_list[-1]["end"] <= gap:
        active_meeting = meetings_list.pop()

    # Format for JSON response
    result = {
        "meetings": [
            {
                "start": m["start"].isoformat(),
                "end": m["end"].isoformat(),
                "duration_minutes": (m["end"] - m["start"]).total_seconds() / 60
            }
            for m in meetings_list
        ],
        "active_meeting": {
            "start": active_meeting["start"].isoformat(),
            "duration_minutes": (now - active_meeting["start"]).total_seconds() / 60
        } if active_meeting else None
    }

    return JsonResponse(result)


def index(request):
    return render(request, 'activity/index.html')