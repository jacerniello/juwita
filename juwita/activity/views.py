from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import datetime
from .models import Log, Meeting, MeetingPhoto
import json


def require_admin(view_func):
    """Decorator to require admin authentication."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


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
def meeting_detail(request, meeting_id):
    """Get, update, or delete a meeting."""
    try:
        meeting = Meeting.objects.get(id=meeting_id)
    except Meeting.DoesNotExist:
        return JsonResponse({"error": "Meeting not found"}, status=404)

    if request.method == "GET":
        photos = [{"id": p.id, "url": p.image.url} for p in meeting.photos.all()]
        return JsonResponse({
            "id": meeting.id,
            "start": meeting.start_time.isoformat(),
            "end": meeting.end_time.isoformat() if meeting.end_time else None,
            "notes": meeting.notes,
            "photos": photos,
            "duration_minutes": meeting.duration.total_seconds() / 60
        })

    elif request.method == "PATCH":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        data = json.loads(request.body)
        if "notes" in data:
            meeting.notes = data["notes"]
        if "start" in data:
            meeting.start_time = datetime.fromisoformat(data["start"].replace('Z', '+00:00'))
        if "end" in data:
            meeting.end_time = datetime.fromisoformat(data["end"].replace('Z', '+00:00'))
        meeting.save()
        return JsonResponse({"success": True})

    elif request.method == "DELETE":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        meeting.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def meeting_photos(request, meeting_id):
    """Upload photos to a meeting."""
    try:
        meeting = Meeting.objects.get(id=meeting_id)
    except Meeting.DoesNotExist:
        return JsonResponse({"error": "Meeting not found"}, status=404)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        if "photo" not in request.FILES:
            return JsonResponse({"error": "No photo provided"}, status=400)
        photo = MeetingPhoto.objects.create(meeting=meeting, image=request.FILES["photo"])
        return JsonResponse({"success": True, "photo_id": photo.id, "url": photo.image.url})

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def delete_photo(request, meeting_id, photo_id):
    """Delete a photo from a meeting."""
    if request.method == "DELETE":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        try:
            photo = MeetingPhoto.objects.get(id=photo_id, meeting_id=meeting_id)
            photo.image.delete()
            photo.delete()
            return JsonResponse({"success": True})
        except MeetingPhoto.DoesNotExist:
            return JsonResponse({"error": "Photo not found"}, status=404)
    return JsonResponse({"error": "Invalid request"}, status=400)


def auth_status(request):
    """Check if user is authenticated."""
    return JsonResponse({
        "authenticated": request.user.is_authenticated,
        "username": request.user.username if request.user.is_authenticated else None
    })


@csrf_exempt
def auth_login(request):
    """Login endpoint."""
    if request.method == "POST":
        data = json.loads(request.body)
        user = authenticate(request, username=data.get("username"), password=data.get("password"))
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True, "username": user.username})
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    return JsonResponse({"error": "Invalid request"}, status=400)


def auth_logout(request):
    """Logout endpoint."""
    logout(request)
    return JsonResponse({"success": True})


def index(request):
    return render(request, 'activity/index.html')
