from django.db.transaction import atomic
from django.shortcuts import render, get_object_or_404

from .models import Content, Fetch, Location


def content_info(request, digest):
    content = get_object_or_404(Content, hash=digest)
    ctx = {
        'content': content,
    }
    return render(request, 'catalog/content_info.html', ctx)


def url_info(request):
    url = request.get_full_path()[1:]
    location, _ = Location.objects.get_or_create(url=url)
    fetches = location.fetches
    if fetches.accepted.count() > 0:
        fetch = fetches.accepted.latest()
    elif fetches.unfinished.count() > 0:
        fetch = fetches.unfinished.latest()
    elif fetches.count() > 0:
        fetch = fetches.latest()
    else:
        if fetches.count() == 0 or fetches.latest().state != 'succeeded':
            with atomic():
                fetch = fetches.create()
                fetch.start()
                fetch.save()
    ctx = {
        'fetch': fetch,
    }
    return render(request, 'catalog/url_info.html', ctx)
