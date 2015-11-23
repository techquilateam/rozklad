import re
from django.db.models import Q
from rest_framework import serializers
from data.models import *

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'okr', 'type')

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ('id', 'name', 'latitude', 'longitude')

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('id', 'name', 'full_name', 'kpimaps_id', 'building')

class NestedRoomSerializer(serializers.ModelSerializer):
    building = BuildingSerializer()

    class Meta:
        model = Room
        fields = ('id', 'name', 'building')

class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = ('id', 'name', 'full_name')

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ('id', 'last_name', 'first_name', 'middle_name', 'name', 'full_name', 'short_name', 'short_name_with_degree', 'degree')

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            'id', 'number', 'day', 'week', 'type', 'discipline_name', 'discipline',
            'groups_names', 'groups', 'teachers_short_names', 'teachers', 'rooms_full_names', 'rooms')

class NestedLessonSerializer(serializers.ModelSerializer):
    discipline = DisciplineSerializer()
    groups = GroupSerializer(many=True)
    teachers = TeacherSerializer(many=True)
    rooms = NestedRoomSerializer(many=True)

    class Meta(LessonSerializer.Meta):
        model = Lesson
        fields = ('id', 'type', 'discipline', 'groups', 'teachers', 'rooms')
