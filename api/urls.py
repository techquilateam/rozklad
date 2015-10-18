from django.conf.urls import include, url
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'groups', views.GroupViewSet)
router.register(r'buildings', views.BuildingViewSet)
router.register(r'rooms', views.RoomViewSet)
router.register(r'disciplines', views.DisciplineViewSet)
router.register(r'teachers', views.TeacherViewSet)
router.register(r'lessons', views.LessonViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
