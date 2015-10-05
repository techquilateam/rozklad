import re
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Group, Building, Room, Discipline, Teacher, Lesson

class GroupSerializer(serializers.ModelSerializer):
    def validate_name(self, value):
        if not re.match('^[0-9a-zA-Zа-яА-ЯёЁіІїЇєЄґҐ\-\(\)]*$', value):
            raise serializers.ValidationError('This value can only contain letters, numbers or -() symbols')

        return value.lower()

    class Meta:
        model = Group
        fields = ('id', 'name', 'okr', 'type')

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ('id', 'number', 'latitude', 'longitude')

class RoomSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if '-' in data['name']:
            try:
                if int(data['name'].split('-')[-1]) != data['building'].number:
                    raise
                else:
                    return data
            except:
                raise serializers.ValidationError('You cannot use \'-\' or a space character. \'-\' before building number will be added automatically')

        data['name'] = data['name'] + '-' + str(data['building'].number)

        return data

    class Meta:
        model = Room
        fields = ('id', 'name', 'building')

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
    def validate_name_part(self, value):
        if not re.match('^[a-zA-Zа-яА-ЯёЁіІїЇєЄґҐ]*$', value):
            raise serializers.ValidationError('This value can only contain letters')

        value_list = list(value.lower())
        value_list[0] = value_list[0].upper()
        return ''.join(value_list)

    validate_last_name = validate_name_part
    validate_first_name = validate_name_part
    validate_middle_name = validate_name_part

    def validate_degree(self, value):
        if not re.match('^[a-zA-Zа-яА-ЯёЁіІїЇєЄґҐ\s]*$', value):
            raise serializers.ValidationError('This value can only contain letters and spaces')

        return value.lower()

    class Meta:
        model = Teacher
        fields = ('id', 'last_name', 'first_name', 'middle_name', 'name', 'full_name', 'short_name', 'degree')

class LessonSerializer(serializers.ModelSerializer):
    def validate(self, data):
        lessons = Lesson.objects.all()

        if self.instance:
            lessons = lessons.filter(~Q(id=self.instance.id))

        lessons = lessons.filter(
            number=data['number'] if 'number' in data.keys() else self.instance.number,
            day=data['day'] if 'day' in data.keys() else self.instance.day,
            week=data['week'] if 'week' in data.keys() else self.instance.week)

        if 'groups' in data.keys():
            for group in data['groups']:
                if lessons.filter(groups=group).exists():
                    lesson = lessons.get(groups=group)
                    raise serializers.ValidationError('Group {0} already have {1} lesson on {2}, {3}'.format(
                        group, lesson.get_number_display(),
                        lesson.get_day_display(), lesson.get_week_display()))

        if 'teachers' in data.keys():
            for teacher in data['teachers']:
                if lessons.filter(teachers=teacher).exists():
                    lesson = lessons.get(teachers=teacher)
                    raise serializers.ValidationError('Teacher {0} already have {1} lesson on {2}, {3}'.format(
                        teacher, lesson.get_number_display(),
                        lesson.get_day_display(), lesson.get_week_display()))

        if 'rooms' in data.keys():
            for room in data['rooms']:
                if lessons.filter(rooms=room).exists():
                    lesson = lessons.get(rooms=room)
                    raise serializers.ValidationError('Room {0} already have {1} lesson on {2}, {3}'.format(
                        room, lesson.get_number_display(),
                        lesson.get_day_display(), lesson.get_week_display()))

        return data

    class Meta:
        model = Lesson
        fields = (
            'id', 'number', 'day', 'week', 'type', 'discipline_name', 'discipline',
            'groups_names', 'groups', 'teachers_short_names', 'teachers', 'rooms_names', 'rooms')

class NestedLessonSerializer(serializers.ModelSerializer):
    discipline = DisciplineSerializer()
    groups = GroupSerializer(many=True)
    teachers = TeacherSerializer(many=True)
    rooms = NestedRoomSerializer(many=True)

    class Meta(LessonSerializer.Meta):
        model = Lesson
        fields = ('id', 'type', 'discipline', 'groups', 'teachers', 'rooms')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
