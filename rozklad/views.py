from rest_framework import viewsets, pagination
from .models import Group, Building, Room, Discipline, Teacher
from .serializers import GroupSerializer, BuildingSerializer, RoomSerializer, DisciplineSerializer, TeacherSerializer

class GlobalViewPagination(pagination.LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = GlobalViewPagination

class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    pagination_class = GlobalViewPagination

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    pagination_class = GlobalViewPagination

class DisciplineViewSet(viewsets.ModelViewSet):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer
    pagination_class = GlobalViewPagination

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    pagination_class = GlobalViewPagination
