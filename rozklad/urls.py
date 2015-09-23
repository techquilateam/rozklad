from django.conf.urls import include, url
from django.contrib import admin
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
]
