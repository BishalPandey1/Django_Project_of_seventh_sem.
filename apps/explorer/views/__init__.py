"""Top-level explorer views — one pair per module (GET + HTMX update)."""

import base64
import json
import re

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST

from ._module_common import _module_view, _module_update, _module_snapshot


def _wrapped(module, template):
    @login_required
    def view(request):
        return _module_view(request, module, template)
    return view


def _wrapped_update(module):
    @login_required
    def view(request):
        return _module_update(request, module)
    return view


def _wrapped_snapshot(module):
    @login_required
    def view(request):
        return _module_snapshot(request, module)
    return view


linear_view     = _wrapped("linear",     "linear")
quadratic_view  = _wrapped("quadratic",  "quadratic")
trig_view       = _wrapped("trig",       "trig")
derivative_view = _wrapped("derivative", "derivative")
integral_view   = _wrapped("integral",   "integral")
geometry_view   = _wrapped("geometry",   "geometry")
transform_view  = _wrapped("transform",  "transform")

linear_update     = _wrapped_update("linear")
quadratic_update  = _wrapped_update("quadratic")
trig_update       = _wrapped_update("trig")
derivative_update = _wrapped_update("derivative")
integral_update   = _wrapped_update("integral")
geometry_update   = _wrapped_update("geometry")
transform_update  = _wrapped_update("transform")

linear_snapshot     = _wrapped_snapshot("linear")
quadratic_snapshot  = _wrapped_snapshot("quadratic")
trig_snapshot       = _wrapped_snapshot("trig")
derivative_snapshot = _wrapped_snapshot("derivative")
integral_snapshot   = _wrapped_snapshot("integral")
geometry_snapshot   = _wrapped_snapshot("geometry")
transform_snapshot  = _wrapped_snapshot("transform")


# ─── Module annotations (frozen-diagram whiteboard) ────────────────
# These let the user freeze the current Plotly diagram, draw on top of
# it with the same pen/eraser/colors as the standalone whiteboard, and
# save the result as a WhiteboardDrawing tagged with the module slug.

_DATA_URL_RE = re.compile(r"^data:image/[a-zA-Z0-9+]+;base64,(.*)$", re.S)


def _decode_data_url(data_url):
    if not data_url:
        return b""
    m = _DATA_URL_RE.match(data_url)
    if not m:
        return b""
    try:
        return base64.b64decode(m.group(1))
    except Exception:
        return b""


def _serialize_annotation(drawing):
    return {
        "id": drawing.id,
        "title": drawing.title,
        "module_slug": drawing.module_slug,
        "strokes": json.loads(drawing.strokes_json) if drawing.strokes_json else [],
        "image_url": drawing.image.url if drawing.image else "",
        "updated_at": drawing.updated_at.isoformat() if drawing.updated_at else None,
    }


@login_required
@require_POST
@csrf_protect
def annotation_save(request, module):
    """Save a frozen-diagram annotation.

    Body: JSON ``{title, strokes: [...], background_data_url: "data:image/png;base64,...",
    pk: <int|null>}``. We persist:
      * the stroke list as JSON (so it can be re-edited and re-rendered
        at any size),
      * a flattened PNG of (background + strokes) as the ``image`` field
        (so the row shows up in the standalone whiteboard list with a
        preview thumbnail).
    """
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "invalid json"}, status=400)

    title = (payload.get("title") or f"{module.title()} annotation")[:120].strip()
    if not title:
        title = f"{module.title()} annotation"
    strokes = payload.get("strokes") or []
    bg_url = payload.get("background_data_url") or ""
    if not isinstance(strokes, list):
        return JsonResponse({"ok": False, "error": "strokes must be a list"}, status=400)

    # Render the combined image: draw background + strokes onto a server-
    # side canvas (via Pillow) so the standalone whiteboard list gets a
    # preview thumbnail. Skip silently if Pillow isn't available.
    png_bytes = b""
    try:
        from PIL import Image, ImageDraw  # type: ignore
        bg_bytes = _decode_data_url(bg_url)
        if bg_bytes:
            from io import BytesIO
            bg = Image.open(BytesIO(bg_bytes)).convert("RGBA")
            overlay = Image.new("RGBA", bg.size, (255, 255, 255, 0))
            d = ImageDraw.Draw(overlay)
            for s in strokes:
                if not isinstance(s, dict):
                    continue
                tool = s.get("tool")
                color = s.get("color") or "#1e1e1e"
                size = max(1, int(float(s.get("size") or 3)))
                data = s.get("data") or {}
                if tool in ("pen", "highlighter"):
                    pts = data.get("points") or []
                    if len(pts) >= 2:
                        flat = [(float(p.get("x", 0)), float(p.get("y", 0))) for p in pts]
                        d.line(flat, fill=color, width=size, joint="curve")
                elif tool == "eraser":
                    pts = data.get("points") or []
                    if len(pts) >= 2:
                        flat = [(float(p.get("x", 0)), float(p.get("y", 0))) for p in pts]
                        d.line(flat, fill=(0, 0, 0, 0), width=size, joint="curve")
                elif tool in ("line", "arrow"):
                    x1, y1, x2, y2 = (float(data.get(k, 0)) for k in ("x1", "y1", "x2", "y2"))
                    d.line([(x1, y1), (x2, y2)], fill=color, width=size)
                elif tool == "rect":
                    x1, y1, x2, y2 = (float(data.get(k, 0)) for k in ("x1", "y1", "x2", "y2"))
                    if s.get("fill"):
                        d.rectangle([(x1, y1), (x2, y2)], fill=color)
                    else:
                        d.rectangle([(x1, y1), (x2, y2)], outline=color, width=size)
                elif tool == "circle":
                    x1, y1, x2, y2 = (float(data.get(k, 0)) for k in ("x1", "y1", "x2", "y2"))
                    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                    rx, ry = abs(x2 - x1) / 2, abs(y2 - y1) / 2
                    if s.get("fill"):
                        d.ellipse([(cx - rx, cy - ry), (cx + rx, cy + ry)], fill=color)
                    else:
                        d.ellipse([(cx - rx, cy - ry), (cx + rx, cy + ry)], outline=color, width=size)
                elif tool == "text":
                    x, y = float(data.get("x", 0)), float(data.get("y", 0))
                    txt = data.get("text") or ""
                    if txt:
                        d.text((x, y), txt, fill=color)
            composed = Image.alpha_composite(bg, overlay).convert("RGB")
            from io import BytesIO
            buf = BytesIO()
            composed.save(buf, format="PNG")
            png_bytes = buf.getvalue()
    except Exception:
        # Pillow unavailable or background missing — save JSON only.
        png_bytes = b""

    from whiteboard.models import WhiteboardDrawing
    pk = payload.get("pk")
    if pk:
        drawing = WhiteboardDrawing.objects.filter(pk=pk, user=request.user).first()
        if drawing is None:
            return JsonResponse({"ok": False, "error": "not found"}, status=404)
    else:
        drawing = WhiteboardDrawing(user=request.user, title=title, module_slug=module)
    drawing.title = title
    drawing.module_slug = module
    drawing.strokes_json = json.dumps(strokes)
    if png_bytes:
        if drawing.image:
            drawing.image.delete(save=False)
        drawing.image.save(
            f"module_{module}_{drawing.pk or 'new'}.png",
            ContentFile(png_bytes),
            save=True,
        )
    drawing.save()
    return JsonResponse({
        "ok": True,
        "id": drawing.id,
        "title": drawing.title,
        "module_slug": drawing.module_slug,
        "updated_at": drawing.updated_at.isoformat() if drawing.updated_at else None,
    })


@login_required
@require_GET
def annotation_list(request, module):
    """List the current user's saved annotations for this module."""
    from whiteboard.models import WhiteboardDrawing
    qs = WhiteboardDrawing.objects.filter(
        user=request.user, module_slug=module
    )[:50]
    return JsonResponse({
        "ok": True,
        "module": module,
        "drawings": [_serialize_annotation(d) for d in qs],
    })


@login_required
@require_GET
def annotation_load(request, module, pk):
    """Return one annotation as JSON for the whiteboard engine to load."""
    from whiteboard.models import WhiteboardDrawing
    drawing = WhiteboardDrawing.objects.filter(
        pk=pk, user=request.user, module_slug=module
    ).first()
    if drawing is None:
        return JsonResponse({"ok": False, "error": "not found"}, status=404)
    return JsonResponse({"ok": True, **_serialize_annotation(drawing)})


@login_required
@require_POST
@csrf_protect
def annotation_delete(request, module, pk):
    from whiteboard.models import WhiteboardDrawing
    drawing = WhiteboardDrawing.objects.filter(
        pk=pk, user=request.user, module_slug=module
    ).first()
    if drawing is None:
        return JsonResponse({"ok": False, "error": "not found"}, status=404)
    if drawing.image:
        drawing.image.delete(save=False)
    drawing.delete()
    return JsonResponse({"ok": True, "id": pk})


@login_required
def modules_index(request):
    """Hub page — list of all 7 modules with access info."""
    from apps.explorer.mathlib import ALL_MODULES, MODULE_LABELS, MODULE_GROUPS
    from apps.accounts.models import get_or_create_profile
    profile = get_or_create_profile(request.user)
    cards = []
    metas = [
        ("linear",     "y = m·x + b",           "from-blue-500/20 to-blue-600/10",     "line-chart"),
        ("quadratic",  "a·x² + b·x + c",        "from-violet-500/20 to-violet-600/10", "parentheses"),
        ("trig",       "A·sin(B·x + C) + D",    "from-cyan-500/20 to-cyan-600/10",     "waves"),
        ("derivative", "f′(x) tangent/secant",  "from-orange-500/20 to-orange-600/10", "trending-up"),
        ("integral",   "Riemann sum",           "from-green-500/20 to-green-600/10",   "sigma"),
        ("geometry",   "11 shapes",             "from-pink-500/20 to-pink-600/10",     "shapes"),
        ("transform",  "[a b; c d]·v",          "from-amber-500/20 to-amber-600/10",   "move-3d"),
    ]
    for slug, formula, gradient, icon in metas:
        if profile.has_module_access(slug):
            cards.append({
                "slug": slug,
                "label": MODULE_LABELS[slug],
                "group": MODULE_GROUPS[slug],
                "formula": formula,
                "gradient": gradient,
                "icon": icon,
            })
    return render(request, "explorer/index.html", {"cards": cards})
