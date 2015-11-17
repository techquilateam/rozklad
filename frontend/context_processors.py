from data.models import Group, Teacher
from guardian.shortcuts import get_objects_for_user

def user_edit_allowed(request):
    result = {}
    result['user_edit_allowed'] = {}

    if (not request.user.is_superuser) and request.user.is_authenticated():
        groups = get_objects_for_user(request.user, 'data.edit_group_timetable')
        teachers = get_objects_for_user(request.user, 'data.edit_teacher_timetable')
        result['user_edit_allowed']['groups'] = groups
        result['user_edit_allowed']['teachers'] = teachers

    return result
