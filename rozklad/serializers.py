from django.db.models import Q
from rest_framework import serializers
from .models import Group, Building, Room, Discipline, Teacher, Lesson

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'okr', 'type')

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ('id', 'number', 'latitude', 'longitude')

class RoomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Room
        fields = ('id', 'name', 'full_name', 'building')

class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = ('id', 'name', 'full_name')

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ('id', 'last_name', 'first_name', 'middle_name', 'name', 'full_name', 'short_name', 'degree')

class LessonSerializer(serializers.HyperlinkedModelSerializer):
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
                if lessons.filter(groups=group).count() > 0:
                    lesson = lessons.get(groups=group)
                    raise serializers.ValidationError('Group %s already have %s lesson on %s, %s' % (
                        group, lesson.get_number_display(),
                        lesson.get_day_display(), lesson.get_week_display()))

        if 'teachers' in data.keys():
            for teacher in data['teachers']:
                if lessons.filter(teachers=teacher).count() > 0:
                    raise serializers.ValidationError('ХУЙ НА 2')

        if 'rooms' in data.keys():
            for room in data['rooms']:
                if lessons.filter(rooms=room).count() > 0:
                    raise serializers.ValidationError('ХУЙ НА 3')

        return data

    class Meta:
        model = Lesson
        fields = ('id', 'number', 'day', 'week', 'type', 'discipline', 'groups', 'teachers', 'rooms')
