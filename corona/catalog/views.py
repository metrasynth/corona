from django.http import HttpResponse
from django.shortcuts import render

from .models import Fetch, Location


# Create your views here.
def url_info(request):
    url = request.get_full_path()[1:]
    location, created = Location.objects.get_or_create(url=url)
    if created or location.fetches.count() == 0:
        fetch = Fetch.objects.create(location=location)
        fetch.start()
        # .........
    location = Location.objects.filter(url=url).first()
    if location is None:
        location = Location.objects.create(url=url)
    return HttpResponse('{}'.format(url))
