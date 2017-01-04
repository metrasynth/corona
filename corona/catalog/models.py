from django.db import models
from django.urls import reverse
from django_fsm import FSMField, transition
import os

from .contentstore import content_store


class ContentManager(models.Manager):

    def add_file(self, path):
        digest = content_store.add(path)
        content, created = self.get_or_create(hash=digest, defaults={'valid': True})
        if not created and not content.valid:
            content.valid = True
            content.save()
        return content


class Content(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    hash = models.CharField(max_length=40, unique=True, db_index=True)
    valid = models.BooleanField()
    magic = models.CharField(max_length=4, db_index=True, blank=True, null=True)

    objects = ContentManager()

    def open(self, mode='rb'):
        return content_store.open(self.hash, mode)

    def populate_magic(self):
        if self.magic is None:
            with self.open() as f:
                self.magic = f.read(4).decode('ASCII')
                self.save()

    def file_type(self):
        if self.magic == 'SVOX':
            return 'SunVox Project'
        elif self.magic == 'SSYN':
            return 'SunVox Module'
        else:
            return self.magic

    def get_absolute_url(self):
        return reverse('content_info', kwargs={'digest': self.hash})


class Location(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    url = models.URLField(max_length=1024, unique=True, db_index=True)


FETCH_FINISHED_STATES = {'accepted', 'rejected', 'timed-out'}


class FetchManager(models.Manager):
    @property
    def accepted(self):
        return self.filter(state='accepted')

    @property
    def unfinished(self):
        return self.exclude(state__in=FETCH_FINISHED_STATES)


class Fetch(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    location = models.ForeignKey('Location', related_name='fetches', db_index=True)
    content = models.ForeignKey('Content', related_name='fetches', null=True)
    state = FSMField(default='new')
    rejection_reason = models.CharField(max_length=32, blank=True, null=True)

    objects = FetchManager()

    class Meta:
        get_latest_by = 'created_at'

    @property
    def is_finished(self):
        return self.state in FETCH_FINISHED_STATES

    @transition(state, 'new', 'fetching')
    def start(self):
        from .jobs import perform_fetch
        perform_fetch.delay(self.id)

    @transition(state, 'fetching', 'processing')
    def process(self):
        pass

    @transition(state, '*', 'accepted')
    def accept(self, path):
        self.content = Content.objects.add_file(path)

    @transition(state, '*', 'rejected')
    def reject(self, reason):
        self.rejection_reason = reason

    @transition(state, '*', 'timed-out')
    def timeout(self, reason):
        self.rejection_reason = reason
