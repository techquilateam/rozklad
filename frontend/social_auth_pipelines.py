from guardian.shortcuts import assign_perm
from .models import UnregisteredVKUserTimetablePermissions

def apply_perms(social, *args, **kwargs):
    user = social.user
    for perms in list(UnregisteredVKUserTimetablePermissions.objects.filter(vk_user_id=int(social.uid))):
        for group in perms.groups.all():
            assign_perm('edit_group_timetable', user, group)
        for teacher in perms.teachers.all():
            assign_perm('edit_teacher_timetable', user, teacher)

        perms.delete()
