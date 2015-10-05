from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^(?P<type>groups|teachers|rooms)/(?P<id>[0-9]+)/$', views.timetable),
    url(r'^login/$', views.auth_login),
    url(r'^logout/$', views.auth_logout),
]
