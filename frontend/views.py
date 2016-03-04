import json
import urllib.request
import urllib.parse
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.exceptions import PermissionDenied
from django.conf import settings
from data.models import *
from .forms import EditUserProfile
from .page_cache import get_timetable_cache

page_base_title = 'Розклад КПІ'

def check_captcha(captcha_response):
    captcha_data = bytes(urllib.parse.urlencode({
        'secret': settings.GOOGLE_RECAPTCHA_PRIVATE,
        'response': captcha_response,
    }).encode())
    return json.loads(urllib.request.urlopen('https://www.google.com/recaptcha/api/siteverify', captcha_data).read().decode('utf-8'))['success']

@ensure_csrf_cookie
def error400(request):
    return render(request, 'error.html', {
        'title': page_base_title + ' | 400',
        'error_text': '400',
        'error_text2': 'Bad Request',
    }, status=400)

@ensure_csrf_cookie
def error403(request):
    return render(request, 'error.html', {
        'title': page_base_title + ' | 403',
        'error_text': '403',
        'error_text2': 'Forbidden',
    }, status=403)

@ensure_csrf_cookie
def error404(request):
    return render(request, 'error.html', {
        'title': page_base_title + ' | 404',
        'error_text': '404',
        'error_text2': 'Нажаль, такої сторінки не існує',
    }, status=404)

@ensure_csrf_cookie
def error500(request):
    return render(request, 'error.html', {
        'title': page_base_title + ' | 500',
        'error_text': '500',
        'error_text2': 'Server Error',
    }, status=500)

@ensure_csrf_cookie
def index(request):
    context = {}
    context['title'] = page_base_title
    
    return render(request, 'index.html', context)

@ensure_csrf_cookie
def api(request):
    context = {}
    context['title'] = page_base_title + ' | API'
    context['api_domain'] = settings.API_DOMAIN
    
    return render(request, 'api.html', context)

@ensure_csrf_cookie
def profile(request):
    if not request.user.is_authenticated():
        raise PermissionDenied
    if request.user.social_auth.all().count() > 0:
        raise PermissionDenied

    context = {}
    context['user_form'] = EditUserProfile(instance=request.user)
    context['title'] = page_base_title + ' | Редагування аккаунту'

    return render(request, 'profile.html', context)

@ensure_csrf_cookie
def timetable(request, type, id):
    context = {}

    context['id'] = id
    context['type'] = type
    context['top_menu_str'] = ''

    if type == 'groups':
        if not Group.objects.filter(id=id).exists():
            raise Http404()
        context['top_menu_str'] = Group.objects.get(id=id).name.upper()
    elif type == 'teachers':
        if not Teacher.objects.filter(id=id).exists():
            raise Http404()
        context['top_menu_str'] = Teacher.objects.get(id=id).name().upper()
    else:
        if not Room.objects.filter(id=id).exists():
            raise Http404()
        context['top_menu_str'] = Room.objects.get(id=id).full_name().upper()
    context['title'] = 'Розклад КПІ | ' + context['top_menu_str']

    queryset = None
    if type == 'groups':
        queryset = Lesson.objects.filter(groups=Group.objects.get(id=id))
    elif type == 'teachers':
        queryset = Lesson.objects.filter(teachers=Teacher.objects.get(id=id))
    else:
        queryset = Lesson.objects.filter(rooms=Room.objects.get(id=id))

    if ((type == 'groups' and (request.user.has_perm('edit_group_timetable', Group.objects.get(id=id)) or request.user.has_perm('data.edit_group_timetable'))) or
        (type == 'teachers' and (request.user.has_perm('edit_teacher_timetable', Teacher.objects.get(id=id)) or request.user.has_perm('data.edit_teacher_timetable')))):
        
        initial_data = {}
        initial_data['groups'] = []
        initial_data['teachers'] = []
        initial_data['rooms'] = []
        initial_data['disciplines'] = []
        for lesson in queryset:
            for group in lesson.groups.all():
                group_dict = {
                    'id': group.id,
                    'name': group.name,
                }

                if group_dict not in initial_data['groups']:
                    initial_data['groups'].append(group_dict)

            for teacher in lesson.teachers.all():
                teacher_dict = {
                    'id': teacher.id,
                    'name': teacher.name(),
                }

                if teacher_dict not in initial_data['teachers']:
                    initial_data['teachers'].append(teacher_dict)

            for room in lesson.rooms.all():
                room_dict = {
                    'id': room.id,
                    'name': room.full_name(),
                }

                if room_dict not in initial_data['rooms']:
                    initial_data['rooms'].append(room_dict)
        
            discipline_dict = {
                'id': lesson.discipline.id,
                'name': lesson.discipline.name,
            }

            if discipline_dict not in initial_data['disciplines']:
                initial_data['disciplines'].append(discipline_dict)

        context['initial_data'] = json.dumps(initial_data)

        context['timetable'] = []

        for week_choice in Lesson.WEEK_CHOICES:
            week = week_choice[0] - 1
            context['timetable'].append([])

            for day_choice in Lesson.DAY_CHOICES:
                day = day_choice[0] - 1
                context['timetable'][week].append([])

                for number_choice in Lesson.NUMBER_CHOICES:
                    number = number_choice[0] - 1

                    if queryset.filter(week=week + 1, day=day + 1, number=number + 1).exists():
                        context['timetable'][week][day].append(queryset.get(week=week + 1, day=day + 1, number=number + 1))
                    else:
                        context['timetable'][week][day].append(None)

        return render(request, 'timetable_edit.html', context)
    else:
        if queryset.count() == 0:
            context['error_text'] = 'Нажаль, розклад відсутній :('
            context['error_text2'] = 'Зверніться до адміністраторів'

            return render(request, 'error.html', context)

        if not get_timetable_cache(type, id):
            context['timetable'] = []

            for week_choice in Lesson.WEEK_CHOICES:
                week = week_choice[0] - 1
                context['timetable'].append([])

                for day_choice in Lesson.DAY_CHOICES:
                    day = day_choice[0] - 1
                    context['timetable'][week].append([])

                    for number_choice in Lesson.NUMBER_CHOICES:
                        number = number_choice[0] - 1

                        if queryset.filter(week=week + 1, day=day + 1, number=number + 1).exists():
                            lesson = queryset.get(week=week + 1, day=day + 1, number=number + 1)

                            for i in range(len(context['timetable'][week][day]), number):
                                context['timetable'][week][day].append(None)

                            context['timetable'][week][day].append(lesson)

        return render(request, 'timetable.html', context)
