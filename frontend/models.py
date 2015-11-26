from django.db import models
from django.contrib.auth.models import User
from data.models import Group, Teacher

class UnregisteredVKUserTimetablePermissions(models.Model):
    vk_user_id = models.IntegerField()
    groups = models.ManyToManyField(Group, blank=True)
    teachers = models.ManyToManyField(Teacher, blank=True)

    def groups_str(self):
        str = ''
        for i, group in enumerate(self.groups.all()):
            str += group.name
            if i < self.groups.all().count() - 1:
                str += ', '
        return str

    def teachers_str(self):
        str = ''
        for i, teacher in enumerate(self.teachers.all()):
            str += teacher.short_name()
            if i < self.teachers.all().count() - 1:
                str += ', '
        return str
