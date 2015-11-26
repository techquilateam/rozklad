from guardian.shortcuts import assign_perm
from .models import UnregisteredVKUserTimetablePermissions

def apply_perms(social, *args, **kwargs):
    if UnregisteredVKUserTimetablePermissions.objects.filter(vk_user_id=int(social.uid)).exists():
        perms = UnregisteredVKUserTimetablePermissions.objects.get(vk_user_id=int(social.uid))
        user = social.user

        for group in perms.groups.all():
            assign_perm('edit_group_timetable', user, group)
        for teacher in perms.teachers.all():
            assign_perm('edit_teacher_timetable', user, teacher)

        perms.delete()
