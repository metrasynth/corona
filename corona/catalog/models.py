from django.db import models
from django_fsm import FSMField, transition


class Content(models.Model):
    created_at = models.DateTimeField(auto_created=True)
    hash = models.CharField(max_length=40, unique=True)
    valid = models.BooleanField()

    @property
    def file_type(self):
        pass


class Location(models.Model):
    created_at = models.DateTimeField(auto_created=True)
    url = models.URLField(max_length=1024, unique=True)


class Fetch(models.Model):
    created_at = models.DateTimeField(auto_created=True)
    location = models.ForeignKey('Location', related_name='fetches')
    content = models.ForeignKey('Content', related_name='fetches')
    state = FSMField(default='new')
    rejection_reason = models.CharField(max_length=32)

    @transition(state, 'new', 'fetching')
    def start(self):
        from .jobs import perform_fetch
        perform_fetch.delay(self.id)

    @transition(state, 'fetching', 'processing')
    def process(self):
        pass

    @transition(state, '*', 'done')
    def finish(self):
        pass

    @transition(state, '*', 'rejected')
    def reject(self, reason):
        pass
