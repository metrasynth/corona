import os
from tempfile import mkstemp
from time import sleep

from django.conf import settings
from django.db.transaction import atomic
from django_rq import job
import requests
from rv.api import read_sunvox_file
from rv.errors import RadiantVoicesError

from .models import Fetch


SUPPORTED_MAGICS = {b'SVOX', b'SSYN'}


@job('fetch')
def perform_fetch(fetch_id):
    fetch = Fetch.objects.get(id=fetch_id)
    fd, tempname = mkstemp()
    size = 0
    magic = None
    with os.fdopen(fd, 'wb') as f:
        req = requests.get(fetch.location.url, stream=True)
        for data in req.iter_content(32768):
            if size == 0:
                magic = data[:4]
                if magic not in SUPPORTED_MAGICS:
                    req.close()
                    os.unlink(tempname)
                    with atomic():
                        fetch.reject('unsupported format')
                        fetch.save()
                    return
            f.write(data)
            size = f.tell()
            if size > settings.CATALOG_CONTENT_MAX_SIZE:
                req.close()
                os.unlink(tempname)
                with atomic():
                    fetch.reject('size limit exceeded')
                    fetch.save()
                return
    with atomic():
        fetch.process()
        fetch.save()
    try:
        read_sunvox_file(tempname)
    except RadiantVoicesError:
        with atomic():
            fetch.reject('unreadable file')
            fetch.save()
        return
    with atomic():
        fetch.accept(tempname)
        fetch.save()
        fetch.content.populate_magic()
