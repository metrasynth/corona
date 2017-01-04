from django_rq import job

from .models import Fetch


@job('fetch')
def perform_fetch(fetch_id):
    fetch = Fetch.objects.get(fetch_id)
    # data = requests...
    fetch.process()
    fetch.finish()
    fetch.reject('download timeout')
    fetch.reject('processing timeout')
    fetch.reject('unreadable file')
