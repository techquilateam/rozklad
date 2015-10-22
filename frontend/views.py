import json
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from settings import domains
from data.models import Lesson, Group, Teacher, Room, Building, Discipline

bad_request = HttpResponseBadRequest('Bad request')

def index(request):
    return render(request, 'index.html', {})

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
        context['top_menu_str'] = Room.objects.get(id=id).name.upper()

    queryset = None
    if type == 'groups':
        queryset = Lesson.objects.filter(groups=Group.objects.get(id=id))
    elif type == 'teachers':
        queryset = Lesson.objects.filter(teachers=Teacher.objects.get(id=id))
    else:
        queryset = Lesson.objects.filter(rooms=Room.objects.get(id=id))

    if ((type == 'groups' and (request.user.has_perm('edit_group_timetable', Group.objects.get(id=id)) or request.user.has_perm('data.edit_group_timetable'))) or
        (type == 'teachers' and (request.user.has_perm('edit_teacher_timetable', Teacher.objects.get(id=id)) or request.user.has_perm('data.edit_teacher_timetable'))) or
        (type == 'rooms' and (request.user.has_perm('edit_room_timetable', Room.objects.get(id=id)) or request.user.has_perm('data.edit_room_timetable')))):
        
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
                    'name': room.name,
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

@require_http_methods(['GET'])
def search(request, type):
    if 'search' not in request.GET.keys() or request.GET['search'] == '':
        return bad_request

    search_str = request.GET['search']

    result = {}

    if type == 'groups':
        groups = Group.objects.filter(name__istartswith=search_str)
        result['data'] = [{'id': group.id, 'name': group.name} for group in groups]
    elif type == 'teachers':
        search_parts = search_str.split(' ')
        search_parts = [part for part in search_parts if part != '']

        if len(search_parts) > 0:
            complex_lookup = Q()
            for part in search_parts:
                complex_lookup &= Q(last_name__istartswith=part) | Q(first_name__istartswith=part) | Q(middle_name__istartswith=part)

            teachers = Teacher.objects.filter(complex_lookup)
            result['data'] = [{'id': teacher.id, 'name': teacher.name()} for teacher in teachers]
        else:
            result['data'] = []
    elif type == 'rooms':
        rooms = Room.objects.filter(name__istartswith=search_str)
        result['data'] = [{'id': room.id, 'name': room.name} for room in rooms]
    else:
        search_parts = search_str.split(' ')
        search_parts = [part for part in search_parts if part != '']

        if len(search_parts) > 0:
            complex_lookup = Q()
            for part in search_parts:
                complex_lookup &= Q(name__icontains=part) | Q(full_name__icontains=part)

            disciplines = Discipline.objects.filter(complex_lookup)
            result['data'] = [{'id': discipline.id, 'name': discipline.name} for discipline in disciplines]
        else:
            result['data'] = []

    return JsonResponse(result)

@require_http_methods(['POST'])
def create_lesson(request):
    request_data = json.loads(request.body.decode('utf-8'))

    if request_data['sender'] == 'group':
        group = Group.objects.get(id=int(request_data['id']))

        if not (request.user.has_perm('edit_group_timetable', group) or request.user.has_perm('data.edit_group_timetable')):
            return bad_request

        week = int(request_data['week'])
        day = int(request_data['day'])
        number = int(request_data['number'])

        if Lesson.objects.filter(week=week, day=day, number=number, groups=group).exists():
            return bad_request

        discipline = Discipline.objects.get(id=int(request_data['discipline_id']))

        if int(request_data['y']) == 0:
            link_lessons = Lesson.objects.filter(number=number, day=day, week=week, discipline=discipline)

            if link_lessons.count() > 0:
                response = {'status': 'CAN_LINK'}
                response['lessons'] = []
                
                for lesson in link_lessons:
                    lesson_data = {}
                    lesson_data['id'] = lesson.id
                    lesson_data['number'] = lesson.number
                    lesson_data['day'] = lesson.day
                    lesson_data['week'] = lesson.week
                    lesson_data['type'] = lesson.type
                    lesson_data['discipline_id'] = lesson.discipline.id
                    lesson_data['group_names'] = []
                    for group in lesson.groups.all():
                        lesson_data['group_names'].append(group.name)
                    lesson_data['teacher_names'] = []
                    for teacher in lesson.teachers.all():
                        lesson_data['teacher_names'].append(teacher.short_name())
                    lesson_data['room_names'] = []
                    for room in lesson.rooms.all():
                        lesson_data['room_names'].append(room.name)

                    response['lessons'].append(lesson_data)

                return JsonResponse(response)

        new_lesson = Lesson(number=number, day=day, week=week, discipline=discipline)
        new_lesson.save()
        new_lesson.groups.add(group)

        return JsonResponse({'status': 'OK'})
    else:
        pass

@require_http_methods(['POST'])
def edit_lesson(request):
    request_data = json.loads(request.body.decode('utf-8'))

    return JsonResponse(request_data)

@require_http_methods(['POST'])
def auth_login(request):
    if ('username' in request.POST.keys()) and ('password' in request.POST.keys()):
        username = request.POST['username']
        password = request.POST['password']
        print(username)
        print(password)
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)

            return JsonResponse({'result': 'OK'})
        else:
            return JsonResponse({'result': 'ERROR'})
    else:
        return JsonResponse({'result': 'ERROR'})

def auth_logout(request):
    logout(request)

    return JsonResponse({'result': 'OK'})
