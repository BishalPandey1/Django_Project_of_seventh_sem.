from django.shortcuts import get_object_or_404, render

from .models import ReadingPage


def index(request):
    pages = ReadingPage.objects.all()
    return render(request, "reading/index.html", {"pages": pages})


def detail(request, slug):
    page = get_object_or_404(ReadingPage, slug=slug)
    from .md import markdown
    rendered = markdown(page.body_md)
    return render(request, "reading/detail.html", {"page": page, "html": rendered})
