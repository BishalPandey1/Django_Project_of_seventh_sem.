from django.shortcuts import get_object_or_404, render

from .models import ReadingPage


def index(request):
    pages = list(ReadingPage.objects.all())
    total = len(pages)
    # Annotate with prev/next for the "table of contents" navigation.
    for i, p in enumerate(pages):
        p.prev = pages[i - 1] if i > 0 else None
        p.next = pages[i + 1] if i < total - 1 else None
    return render(request, "reading/index.html", {"pages": pages, "total_chapters": total})


def detail(request, slug):
    page = get_object_or_404(ReadingPage, slug=slug)
    from .md import markdown
    rendered = markdown(page.body_md)
    # Sibling chapters for prev/next navigation.
    siblings = list(ReadingPage.objects.all())
    idx = next((i for i, p in enumerate(siblings) if p.pk == page.pk), 0)
    prev_page = siblings[idx - 1] if idx > 0 else None
    next_page = siblings[idx + 1] if idx < len(siblings) - 1 else None
    return render(request, "reading/detail.html", {
        "page": page,
        "html": rendered,
        "toc_pages": siblings,
        "prev_page": prev_page,
        "next_page": next_page,
        "chapter_index": idx + 1,
        "chapter_total": len(siblings),
    })
