# from django.db import models
# from django_fsm import FSMField, transition
#
#
# class RenderedContent(models.Model):
#     created_at = models.DateTimeField(auto_created=True)
#     source_content = models.ForeignKey('catalog.Content')
#     codec = models.CharField(max_length=10)
#     hash = models.CharField(max_length=40)
#     state = FSMField(default='new')
#     last_accessed_at = models.DateTimeField()
#     last_rendered_at = models.DateTimeField()
#     last_deleted_at = models.DateTimeField()
#
#     class Meta:
#         unique_together = [
#             ('source_content', 'codec'),
#         ]
