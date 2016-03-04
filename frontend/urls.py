from django.conf.urls import include, url
from django.contrib import admin
from . import views, ajax_views

urlpatterns = [
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^$', views.index, name='index'),
    url(r'^(?P<type>groups|teachers|rooms)/(?P<id>[0-9]+)/$', views.timetable, name='timetable'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^api/$', views.api, name='api'),
    url(r'^(?P<type>groups|teachers|rooms|disciplines)/search/$', ajax_views.search, name='search'),
    url(r'^edit-profile/$', ajax_views.edit_profile, name='edit_profile'),
    url(r'^create-lesson/$', ajax_views.create_lesson, name='create_lesson'),
    url(r'^edit-lesson/$', ajax_views.edit_lesson, name='edit_lesson'),
    url(r'^remove-lesson/$', ajax_views.remove_lesson, name='remove_lesson'),
    url(r'^link-lesson/$', ajax_views.link_lesson, name='link_lesson'),
    url(r'^login/$', ajax_views.auth_login, name='login'),
    url(r'^logout/$', ajax_views.auth_logout, name='logout'),
    url(r'^admin/', include(admin.site.urls))
]

handler400 = 'frontend.views.error400'
handler403 = 'frontend.views.error403'
handler404 = 'frontend.views.error404'
handler500 = 'frontend.views.error500'
