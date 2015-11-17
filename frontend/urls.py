from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^$', views.index),
    url(r'^(?P<type>groups|teachers|rooms)/(?P<id>[0-9]+)/$', views.timetable),
    url(r'^(?P<type>groups|teachers|rooms|disciplines)/search/$', views.search),
    url(r'^profile/$', views.profile),
    url(r'^edit-profile/$', views.edit_profile),
    url(r'^create-lesson/$', views.create_lesson),
    url(r'^edit-lesson/$', views.edit_lesson),
    url(r'^remove-lesson/$', views.remove_lesson),
    url(r'^link-lesson/$', views.link_lesson),
    url(r'^login/$', views.auth_login),
    url(r'^logout/$', views.auth_logout),
    url(r'^admin/', include(admin.site.urls)),
]

handler404 = 'frontend.views.error'
