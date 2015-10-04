from django.conf.urls import include, url
from django.contrib import admin
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'groups', views.GroupViewSet)
router.register(r'buildings', views.BuildingViewSet)
router.register(r'rooms', views.RoomViewSet)
router.register(r'disciplines', views.DisciplineViewSet)
router.register(r'teachers', views.TeacherViewSet)
router.register(r'lessons', views.LessonViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    url(r'^$', views.ApiRoot.as_view()),
    url(r'^', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
]

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
