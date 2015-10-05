from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^groups/(?P<id>[0-9]+)/$', views.group),
]
