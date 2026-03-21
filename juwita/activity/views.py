from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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

def index(request):
    return render(request, 'activity/index.html')