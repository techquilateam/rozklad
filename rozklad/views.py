from collections import OrderedDict
from django.contrib.auth.models import User
from rest_framework import viewsets, pagination, filters, permissions
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from .models import Group, Building, Room, Discipline, Teacher, Lesson
from . import serializers
from . import permissions as rozklad_permissions

def get_serializer_class(self):
    if not self.request.user.is_superuser:
        return self.serializer_class

    class AdminSerializerClass(self.serializer_class):
        class Meta(self.serializer_class.Meta):
            fields = self.serializer_class.Meta.fields + ('moderators',)

    return AdminSerializerClass

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

class ApiRoot(APIView):
    def get(self, request, format=None):
        api_root_dict = OrderedDict()
        
        api_root_dict['groups'] = reverse('group-list', request=request, format=format)
        api_root_dict['buildings'] = reverse('building-list', request=request, format=format)
        api_root_dict['rooms'] = reverse('room-list', request=request, format=format)
        api_root_dict['disciplines'] = reverse('discipline-list', request=request, format=format)
        api_root_dict['teachers'] = reverse('teacher-list', request=request, format=format)
        api_root_dict['lessons'] = reverse('lesson-list', request=request, format=format)
        
        if request.user.is_authenticated():
            api_root_dict['users'] = reverse('user-list', request=request, format=format)

        return Response(api_root_dict)

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    pagination_class = GlobalViewPagination

    permission_classes = (rozklad_permissions.IsAdminOrModeratorOrReadOnly,)
    get_serializer_class = get_serializer_class

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

    permission_classes = (rozklad_permissions.IsAdminOrModeratorOrReadOnly,)
    get_serializer_class = get_serializer_class

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

    permission_classes = (rozklad_permissions.IsAdminOrModeratorOrReadOnly,)
    get_serializer_class = get_serializer_class

    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'full_name')

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = serializers.TeacherSerializer
    pagination_class = GlobalViewPagination

    permission_classes = (rozklad_permissions.IsAdminOrModeratorOrReadOnly,)
    get_serializer_class = get_serializer_class

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

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer

    permission_classes = (permissions.IsAuthenticated,)
