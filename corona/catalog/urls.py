from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<digest>[0-9a-f]{40})/$', views.content_info, name='content_info'),
    url(r'^(?:https?)://.+$', views.url_info, name='url_info'),
]
