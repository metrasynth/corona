from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?:http|https)://.+$', views.url_info),
]
