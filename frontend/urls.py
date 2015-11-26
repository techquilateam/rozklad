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
    url(r'^api/$', views.api),
    url(r'^admin/', include(admin.site.urls))
]

handler400 = 'frontend.views.error400'
handler403 = 'frontend.views.error403'
handler404 = 'frontend.views.error404'
handler500 = 'frontend.views.error500'
