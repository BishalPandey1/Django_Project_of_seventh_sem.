import base64
import json

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST

from .models import WhiteboardDrawing


def _serialize_drawing(d):
    return {
        "id": d.id,
        "title": d.title,
        "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        "url": f"/board/?drawing={d.id}",
    }


def whiteboard_page(request):
    drawings = []
    if request.user.is_authenticated:
        drawings = WhiteboardDrawing.objects.filter(user=request.user)[:20]
    return render(request, "whiteboard/page.html", {
        "drawings": drawings,
        "variant": "page",
    })


def whiteboard_overlay(request):
    return render(request, "whiteboard/overlay.html", {"variant": "overlay"})


def whiteboard_annotate(request):
    return render(request, "whiteboard/annotate_demo.html")


@login_required
@require_POST
@csrf_protect
def whiteboard_save(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "invalid json"}, status=400)

    title = (payload.get("title") or "Untitled")[:120].strip() or "Untitled"
    data_url = payload.get("data_url") or ""
    if "," in data_url:
        data_url = data_url.split(",", 1)[1]
    try:
        raw = base64.b64decode(data_url)
    except Exception:
        return JsonResponse({"ok": False, "error": "invalid data_url"}, status=400)
    if not raw:
        return JsonResponse({"ok": False, "error": "empty image"}, status=400)

    pk = payload.get("pk")
    if pk:
        drawing = get_object_or_404(WhiteboardDrawing, pk=pk, user=request.user)
        drawing.title = title
    else:
        drawing = WhiteboardDrawing(user=request.user, title=title)

    if drawing.image:
        drawing.image.delete(save=False)
    drawing.image.save(f"board_{drawing.pk or 'new'}.png", ContentFile(raw), save=True)
    return JsonResponse({
        "ok": True,
        "id": drawing.id,
        "title": drawing.title,
        "updated_at": drawing.updated_at.isoformat() if drawing.updated_at else None,
    })


@require_GET
def whiteboard_load(request, pk):
    drawing = get_object_or_404(WhiteboardDrawing, pk=pk)
    if drawing.image:
        with drawing.image.open("rb") as f:
            data = base64.b64encode(f.read()).decode("ascii")
        return JsonResponse({
            "id": drawing.id,
            "title": drawing.title,
            "data_url": f"data:image/png;base64,{data}",
        })
    return JsonResponse({"id": drawing.id, "title": drawing.title, "data_url": ""})


@login_required
@require_POST
@csrf_protect
def whiteboard_delete(request, pk):
    drawing = get_object_or_404(WhiteboardDrawing, pk=pk, user=request.user)
    if drawing.image:
        drawing.image.delete(save=False)
    drawing.delete()
    return JsonResponse({"ok": True, "id": pk})
