from rest_framework import viewsets, pagination, filters
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from data.models import *
from . import serializers
from .filters import *

class GlobalViewPagination(pagination.LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

def timetable(request, lessons):
    result = {}
    result['data'] = {}
    
    for week_choice in Lesson.WEEK_CHOICES:
        for day_choice in Lesson.DAY_CHOICES:
            for number_choice in Lesson.NUMBER_CHOICES:
                if lessons.filter(week=week_choice[0], day=day_choice[0], number=number_choice[0]).exists():
                    if week_choice[0] not in result['data'].keys():
                        result['data'][week_choice[0]] = {}
                    if day_choice[0] not in result['data'][week_choice[0]].keys():
                        result['data'][week_choice[0]][day_choice[0]] = {}

                    result_day = result['data'][week_choice[0]][day_choice[0]]

                    lesson = lessons.get(week=week_choice[0], day=day_choice[0], number=number_choice[0])
                    lesson_serializer = serializers.NestedLessonSerializer(lesson, context={'request': request})
                    result_day[number_choice[0]] = lesson_serializer.data

    return Response(result)

class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    pagination_class = GlobalViewPagination

    filter_backends = (SearchGroupFilterBackend, filters.DjangoFilterBackend)
    filter_fields = ('name', 'okr', 'type')

    @detail_route(methods=['GET'])
    def timetable(self, request, pk, format=None):
        return timetable(request, Lesson.objects.filter(groups=Group.objects.get(pk=pk)))

class BuildingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Building.objects.all()
    serializer_class = serializers.BuildingSerializer
    pagination_class = GlobalViewPagination

class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Room.objects.all()
    serializer_class = serializers.RoomSerializer
    pagination_class = GlobalViewPagination

    filter_backends = (SearchRoomFilterBackend, filters.DjangoFilterBackend)
    filter_fields = ('name', 'building')

    @detail_route(methods=['GET'])
    def timetable(self, request, pk, format=None):
        return timetable(request, Lesson.objects.filter(rooms=Room.objects.get(pk=pk)))

class DisciplineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Discipline.objects.all()
    serializer_class = serializers.DisciplineSerializer
    pagination_class = GlobalViewPagination

    filter_backends = (SearchDisciplineFilterBackend,)

class TeacherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = serializers.TeacherSerializer
    pagination_class = GlobalViewPagination

    filter_backends = (SearchTeacherFilterBackend,)

    @detail_route(methods=['GET'])
    def timetable(self, request, pk, format=None):
        return timetable(request, Lesson.objects.filter(teachers=Teacher.objects.get(pk=pk)))

class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = serializers.LessonSerializer
    pagination_class = GlobalViewPagination

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('number', 'day', 'week', 'type', 'discipline', 'groups', 'teachers', 'rooms')
