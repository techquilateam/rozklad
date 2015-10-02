from rest_framework import viewsets, pagination, filters
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from .models import Group, Building, Room, Discipline, Teacher, Lesson
from . import serializers

def timetable(request, lessons):
    result = {}
    result['data'] = {}
    
    for week_choice in Lesson.WEEK_CHOICES:
        result['data'][week_choice[0]] = {}
        result_week = result['data'][week_choice[0]]

        for day_choice in Lesson.DAY_CHOICES:
            result_week[day_choice[0]] = {}
            result_day = result_week[day_choice[0]]

            for number_choice in Lesson.NUMBER_CHOICES:
                if lessons.filter(week=week_choice[0], day=day_choice[0], number=number_choice[0]).count() > 0:
                    lesson = lessons.get(week=week_choice[0], day=day_choice[0], number=number_choice[0])
                    lesson_serializer = serializers.NestedLessonSerializer(lesson, context={'request': request})
                    result_day[number_choice[0]] = lesson_serializer.data
                else:
                    result_day[number_choice[0]] = {}

    return Response(result)

class GlobalViewPagination(pagination.LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    pagination_class = GlobalViewPagination

    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    search_fields = ('^name',)
    filter_fields = ('name', 'okr', 'type')

    @detail_route(methods=['GET'])
    def timetable(self, request, pk, format=None):
        return timetable(request, Lesson.objects.filter(groups=Group.objects.get(pk=pk)))

class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = serializers.BuildingSerializer
    pagination_class = GlobalViewPagination

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = serializers.RoomSerializer
    pagination_class = GlobalViewPagination

    filter_backends = (filters.SearchFilter, filters.DjangoFilterBackend)
    search_fields = ('^name')
    filter_fields = ('name', 'building')

    @detail_route(methods=['GET'])
    def timetable(self, request, pk, format=None):
        return timetable(request, Lesson.objects.filter(rooms=Room.objects.get(pk=pk)))

class DisciplineViewSet(viewsets.ModelViewSet):
    queryset = Discipline.objects.all()
    serializer_class = serializers.DisciplineSerializer
    pagination_class = GlobalViewPagination

    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'full_name')

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = serializers.TeacherSerializer
    pagination_class = GlobalViewPagination

    filter_backends = (filters.SearchFilter,)
    search_fields = ('^last_name', '^first_name', '^middle_name')

    @detail_route(methods=['GET'])
    def timetable(self, request, pk, format=None):
        return timetable(request, Lesson.objects.filter(teachers=Teacher.objects.get(pk=pk)))

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = serializers.LessonSerializer
    pagination_class = GlobalViewPagination

    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('number', 'day', 'week', 'type', 'discipline', 'groups', 'teachers', 'rooms')
