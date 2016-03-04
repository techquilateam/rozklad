from django.conf import settings
from data.models import Group, Teacher
from guardian.shortcuts import get_objects_for_user

def google_keys(request):
    return {
        'google_analytics_identificator': settings.GOOGLE_ANALYTICS_IDENTIFICATOR,
        'google_recaptcha_public': settings.GOOGLE_RECAPTCHA_PUBLIC,
    }

def user_edit_allowed(request):
    context = {}
    context['user_edit_allowed'] = {}

    if (not request.user.is_superuser) and request.user.is_authenticated():
        groups = get_objects_for_user(request.user, 'data.edit_group_timetable')
        teachers = get_objects_for_user(request.user, 'data.edit_teacher_timetable')
        context['user_edit_allowed']['groups'] = groups
        context['user_edit_allowed']['teachers'] = teachers

    return context
