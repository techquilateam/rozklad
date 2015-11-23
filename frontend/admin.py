from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from functools import partial
from data.models import Building, Room, Group, Teacher, Discipline, Lesson

class BuildingAdmin(GuardedModelAdmin):
    list_display = ('name', 'latitude', 'longitude')

class RoomAdmin(GuardedModelAdmin):
    list_display = ('name', 'building')
    list_filter = ('building',)
    search_fields = ('^name',)

class DisciplineAdmin(GuardedModelAdmin):
    list_display = ('name', 'full_name')
    search_fields = ('name', 'full_name')

class GroupAdmin(GuardedModelAdmin):
    list_display = ('name', 'okr', 'type')
    list_filter = ('okr', 'type')
    search_fields = ('^name',)

class TeacherAdmin(GuardedModelAdmin):
    list_display = ('name', 'last_name', 'first_name', 'middle_name', 'degree', 'full_name', 'short_name')
    search_fields = ('^last_name', '^first_name', '^middle_name')

class LessonAdmin(GuardedModelAdmin):
    list_display = ('number', 'day', 'week', 'type', 'discipline')
    list_filter = ['groups', 'teachers', 'rooms']
    filter_horizontal = ['groups', 'teachers', 'rooms']

admin.site.register(Building, BuildingAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Discipline, DisciplineAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Lesson, LessonAdmin)
