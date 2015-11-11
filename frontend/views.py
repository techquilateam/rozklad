import json
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.core.cache import caches
from django.views.decorators.csrf import ensure_csrf_cookie
from settings import domains
from data.models import *
from data.search import *

bad_request = HttpResponseBadRequest('Bad request')
forbidden_request = HttpResponseForbidden('Forbidden')

@ensure_csrf_cookie
def index(request):
    return render(request, 'index.html', {})

@ensure_csrf_cookie
def timetable(request, type, id):
    cache = caches['default']
    cache_key = 'timetable_{0}_{1}'.format(type, str(id))

    cache_res = cache.get(cache_key)
    if (request.user.is_anonymous() and
        (cache_res != None)):
        return cache_res
    else:
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

            page = render(request, 'timetable.html', context)
            if request.user.is_anonymous():
                cache.set(cache_key, page, 1800)
            return page

max_results = 10

@require_http_methods(['GET'])
def search(request, type):
    if 'search' not in request.GET.keys() or request.GET['search'] == '':
        return bad_request

    search_str = request.GET['search']

    result = {}

    if type == 'groups':
        groups = search_group(search_str, Group.objects.all())[:max_results]
        result['data'] = [{'id': group.id, 'name': group.name} for group in groups]
    elif type == 'teachers':
        teachers = search_teacher(search_str, Teacher.objects.all())[:max_results]
        result['data'] = [{'id': teacher.id, 'name': teacher.name()} for teacher in teachers]
    elif type == 'rooms':
        rooms = search_room(search_str, Room.objects.all())[:max_results]
        result['data'] = [{'id': room.id, 'name': room.full_name()} for room in rooms]
    else:
        disciplines = search_discipline(search_str, Discipline.objects.all())[:max_results]
        result['data'] = [{'id': discipline.id, 'name': discipline.name} for discipline in disciplines]

    return JsonResponse(result)

@require_http_methods(['POST'])
def create_lesson(request):
    request_data = json.loads(request.body.decode('utf-8'))

    if request_data['sender'] == 'group':
        current_group = Group.objects.get(id=request_data['id'])

        if not (request.user.has_perm('edit_group_timetable', current_group) or request.user.has_perm('data.edit_group_timetable')):
            return forbidden_request

        week = request_data['week']
        day = request_data['day']
        number = request_data['number']
        another_week = True if request_data['another_week'] == 1 else False
        
        if ((not another_week) and Lesson.objects.filter(week=week, day=day, number=number, groups=current_group).exists()):
            return bad_request
        elif (another_week and Lesson.objects.filter(day=day, number=number, groups=current_group).exists()):
            return bad_request

        discipline = Discipline.objects.get(id=request_data['discipline_id'])

        if request_data['y'] == 0:
            if another_week:
                link_lessons = Lesson.objects.filter(number=number, day=day, discipline=discipline)
                link_lessons_groups = set()
                for lesson in link_lessons:
                    for group in lesson.groups.all():
                        link_lessons_groups.add(group)

                link_lessons_pairs = set()
                for group in link_lessons_groups:
                    group_lessons = link_lessons.filter(groups=group)
                    if group_lessons.count() == 2:
                        link_lessons_pairs.add(frozenset(group_lessons))
                link_lessons_pairs = [tuple(lesson_pair) for lesson_pair in link_lessons_pairs]

                if len(link_lessons_pairs) > 0:
                    response = {'status': 'CAN_LINK'}
                    response['lessons'] = []

                    for lesson_pair in link_lessons_pairs:
                        lesson_data = {}
                        lesson_data['id'] = lesson_pair[0].id
                        lesson_data['second_id'] = lesson_pair[1].id
                        lesson_data['number'] = lesson_pair[0].number
                        lesson_data['day'] = lesson_pair[0].day
                        lesson_data['type'] = lesson_pair[0].type
                        lesson_data['discipline_name'] = lesson_pair[0].discipline.name
                        lesson_data['group_names'] = [group.name for group in lesson_pair[0].groups.all() if group in lesson_pair[1].groups.all()]
                        lesson_data['teacher_names'] = [teacher.short_name() for teacher in lesson_pair[0].teachers.all()]
                        lesson_data['room_names'] = [room.full_name() for room in lesson_pair[0].rooms.all()]

                        response['lessons'].append(lesson_data)

                    return JsonResponse(response)
            else:
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
                        lesson_data['discipline_name'] = lesson.discipline.name
                        lesson_data['group_names'] = [group.name for group in lesson.groups.all()]
                        lesson_data['teacher_names'] = [teacher.short_name() for teacher in lesson.teachers.all()]
                        lesson_data['room_names'] = [room.full_name() for room in lesson.rooms.all()]

                        response['lessons'].append(lesson_data)

                    return JsonResponse(response)

        if another_week:
            first_new_lesson = Lesson(number=number, day=day, week=1, discipline=discipline)
            first_new_lesson.save()
            first_new_lesson.groups.add(current_group)
            second_new_lesson = Lesson(number=number, day=day, week=2, discipline=discipline)
            second_new_lesson.save()
            second_new_lesson.groups.add(current_group)
        else:
            new_lesson = Lesson(number=number, day=day, week=week, discipline=discipline)
            new_lesson.save()
            new_lesson.groups.add(current_group)

        cache = caches['default']

        cache.delete('timetable_groups_{0}'.format(str(current_group.id)))

        return JsonResponse({'status': 'OK'})
    else:
        pass

@require_http_methods(['POST'])
def edit_lesson(request):
    request_data = json.loads(request.body.decode('utf-8'))

    if request_data['sender'] == 'group':
        current_group = Group.objects.get(id=request_data['id'])
        current_lesson = Lesson.objects.get(id=request_data['lesson_id'])
        if current_group not in current_lesson.groups.all():
            return bad_request

        if not (request.user.has_perm('edit_group_timetable', current_group) or request.user.has_perm(data.edit_group_timetable)):
            return forbidden_request

        old_teachers_id = [teacher.id for teacher in current_lesson.teachers.all()]
        old_rooms_id = [room.id for room in current_lesson.rooms.all()]
        new_teachers_id = request_data['teachers_id']
        new_rooms_id = request_data['rooms_id']

        add_teachers_id = [id for id in new_teachers_id if id not in old_teachers_id]
        remove_teachers_id = [id for id in old_teachers_id if id not in new_teachers_id]
        static_teachers_id = [id for id in new_teachers_id if id in old_teachers_id]
        add_rooms_id = [id for id in new_rooms_id if id not in old_rooms_id]
        remove_rooms_id = [id for id in old_rooms_id if id not in new_rooms_id]
        static_rooms_id = [id for id in new_rooms_id if id in old_rooms_id]

        group_exclude_lesson_queryset = Lesson.objects.all()
        for group in current_lesson.groups.all():
            group_exclude_lesson_queryset = group_exclude_lesson_queryset.filter(~Q(groups=group))

        for teacher_id in new_teachers_id:
            teacher = Teacher.objects.get(id=teacher_id)
            if group_exclude_lesson_queryset.filter(number=current_lesson.number, day=current_lesson.day, week=current_lesson.week, teachers=teacher).exists():
                return JsonResponse({
                    'status': 'ERROR',
                    'error_code': 0,
                    'teacher_name': teacher.name(),
                })

        for room_id in new_rooms_id:
            room = Room.objects.get(id=room_id)
            if group_exclude_lesson_queryset.filter(number=current_lesson.number, day=current_lesson.day, week=current_lesson.week, rooms=room).exists():
                return JsonResponse({
                    'status': 'ERROR',
                    'error_code': 1,
                    'room_name': room.name,
                })

        type_choices_keys = [choice[0] for choice in Lesson.TYPE_CHOICES]
        
        current_lesson_type = None
        if request_data['lesson_type'] == 'None':
            pass
        elif int(request_data['lesson_type']) in type_choices_keys:
            current_lesson_type = int(request_data['lesson_type'])
        else:
            return bad_request

        another_week = True if request_data['another_week'] == 1 else False

        current_lesson_2 = None
        add_teachers_id_2 = None
        remove_teachers_id_2 = None
        static_teachers_id_2 = None
        add_rooms_id_2 = None
        remove_rooms_id_2 = None
        static_rooms_id_2 = None
        if another_week:
            another_week_number = 2 if current_lesson.week == 1 else 1

            current_lesson_2 = Lesson.objects.get(number=current_lesson.number, day=current_lesson.day, week=another_week_number, groups=current_group)

            old_teachers_id_2 = [teacher.id for teacher in current_lesson_2.teachers.all()]
            old_rooms_id_2 = [room.id for room in current_lesson_2.rooms.all()]

            add_teachers_id_2 = [id for id in new_teachers_id if id not in old_teachers_id_2]
            remove_teachers_id_2 = [id for id in old_teachers_id_2 if id not in new_teachers_id]
            static_teachers_id_2 = [id for id in new_teachers_id if id in old_teachers_id_2]
            add_rooms_id_2 = [id for id in new_rooms_id if id not in old_rooms_id_2]
            remove_rooms_id_2 = [id for id in old_rooms_id_2 if id not in new_rooms_id]
            static_rooms_id_2 = [id for id in new_rooms_id if id in old_rooms_id_2]

            group_exclude_lesson_queryset_2 = Lesson.objects.all()
            for group in current_lesson_2.groups.all():
                group_exclude_lesson_queryset_2 = group_exclude_lesson_queryset_2.filter(~Q(groups=group))

            for teacher_id in new_teachers_id:
                teacher = Teacher.objects.get(id=teacher_id)
                if group_exclude_lesson_queryset_2.filter(number=current_lesson_2.number, day=current_lesson_2.day, week=current_lesson_2.week, teachers=teacher).exists():
                    return JsonResponse({
                        'status': 'ERROR',
                        'error_code': 0,
                        'teacher_name': teacher.name(),
                    })

            for room_id in new_rooms_id:
                room = Room.objects.get(id=room_id)
                if group_exclude_lesson_queryset_2.filter(number=current_lesson_2.number, day=current_lesson_2.day, week=current_lesson_2.week, rooms=room).exists():
                    return JsonResponse({
                        'status': 'ERROR',
                        'error_code': 1,
                        'room_name': room.name,
                    })

        cache = caches['default']

        current_lesson.type = current_lesson_type
        current_lesson.save()

        for teacher_id in remove_teachers_id:
            current_lesson.teachers.remove(Teacher.objects.get(id=teacher_id))
            cache.delete('timetable_teachers_{0}'.format(str(teacher_id)))
        for room_id in remove_rooms_id:
            current_lesson.rooms.remove(Room.objects.get(id=room_id))
            cache.delete('timetable_rooms_{0}'.format(str(room_id)))

        for teacher_id in add_teachers_id:
            current_lesson.teachers.add(Teacher.objects.get(id=teacher_id))
            cache.delete('timetable_teachers_{0}'.format(str(teacher_id)))
        for room_id in add_rooms_id:
            current_lesson.rooms.add(Room.objects.get(id=room_id))
            cache.delete('timetable_rooms_{0}'.format(str(room_id)))

        for teacher_id in static_teachers_id:
            cache.delete('timetable_teachers_{0}'.format(str(teacher_id)))
        for room_id in static_rooms_id:
            cache.delete('timetable_rooms_{0}'.format(str(room_id)))

        for group_id in [group.id for group in current_lesson.groups.all()]:
            cache.delete('timetable_groups_{0}'.format(str(group_id)))

        if another_week:
            current_lesson_2.type = current_lesson_type
            current_lesson_2.save()

            for teacher_id in remove_teachers_id_2:
                current_lesson_2.teachers.remove(Teacher.objects.get(id=teacher_id))
                cache.delete('timetable_teachers_{0}'.format(str(teacher_id)))
            for room_id in remove_rooms_id_2:
                current_lesson_2.rooms.remove(Room.objects.get(id=room_id))
                cache.delete('timetable_rooms_{0}'.format(str(room_id)))

            for teacher_id in add_teachers_id_2:
                current_lesson_2.teachers.add(Teacher.objects.get(id=teacher_id))
                cache.delete('timetable_teachers_{0}'.format(str(teacher_id)))
            for room_id in add_rooms_id_2:
                current_lesson_2.rooms.add(Room.objects.get(id=room_id))
                cache.delete('timetable_rooms_{0}'.format(str(room_id)))

            for teacher_id in static_teachers_id_2:
                cache.delete('timetable_teachers_{0}'.format(str(teacher_id)))
            for room_id in static_rooms_id_2:
                cache.delete('timetable_rooms_{0}'.format(str(room_id)))

            for group_id in [group.id for group in current_lesson_2.groups.all()]:
                cache.delete('timetable_groups_{0}'.format(str(group_id)))

        return JsonResponse({'status': 'OK'})
    else:
        pass

@require_http_methods(['POST'])
def remove_lesson(request):
    request_data = json.loads(request.body.decode('utf-8'))

    if request_data['sender'] == 'group':
        current_group = Group.objects.get(id=request_data['id'])

        if not (request.user.has_perm('edit_group_timetable', current_group) or request.user.has_perm('data.edit_group_timetable')):
            return forbidden_request

        current_lesson = Lesson.objects.get(id=request_data['lesson_id'])

        if current_group not in current_lesson.groups.all():
            return bad_request

        another_week = True if request_data['another_week'] == 1 else False

        current_lesson_2 = None
        if another_week:
            another_week_number = 2 if current_lesson.week == 1 else 1

            current_lesson_2 = Lesson.objects.get(number=current_lesson.number, day=current_lesson.day, week=another_week_number, groups=current_group)

        cache = caches['default']

        for group in current_lesson.groups.all():
            cache.delete('timetable_groups_{0}'.format(str(group.id)))
        for teacher in current_lesson.teachers.all():
            cache.delete('timetable_teachers_{0}'.format(str(teacher.id)))
        for room in current_lesson.rooms.all():
            cache.delete('timetable_rooms_{0}'.format(str(room.id)))

        if current_lesson.groups.all().count() == 1:
            current_lesson.delete()
        else:
            current_lesson.groups.remove(current_group)

        if another_week:
            for group in current_lesson_2.groups.all():
                cache.delete('timetable_groups_{0}'.format(str(group.id)))
            for teacher in current_lesson_2.teachers.all():
                cache.delete('timetable_teachers_{0}'.format(str(teacher.id)))
            for room in current_lesson_2.rooms.all():
                cache.delete('timetable_rooms_{0}'.format(str(room.id)))

            if current_lesson_2.groups.all().count() == 1:
                current_lesson_2.delete()
            else:
                current_lesson_2.groups.remove(current_group)

        return JsonResponse({'status': 'OK'})
    else:
        pass

@require_http_methods(['POST'])
def link_lesson(request):
    request_data = json.loads(request.body.decode('utf-8'))

    if request_data['sender'] == 'group':
        current_group = Group.objects.get(id=request_data['id'])

        if not (request.user.has_perm('edit_group_timetable', current_group) or request.user.has_perm('data.edit_group_timetable')):
            return forbidden_request

        another_week = True if request_data['another_week'] == 1 else False

        if another_week:
            first_lesson = Lesson.objects.get(id=request_data['lesson_id'])
            second_lesson = Lesson.objects.get(id=request_data['second_lesson_id'])

            if (first_lesson.number != second_lesson.number or
                first_lesson.day != second_lesson.day or
                first_lesson.discipline != second_lesson.discipline or
                len([group for group in first_lesson.groups.all() if group in second_lesson.groups.all()]) == 0):
                return bad_request

            first_lesson.groups.add(current_group)
            second_lesson.groups.add(current_group)

            cache = caches['default']

            for group in first_lesson.groups.all():
                cache.delete('timetable_groups_{0}'.format(str(group.id)))
            for group in second_lesson.groups.all():
                cache.delete('timetable_groups_{0}'.format(str(group.id)))
            for teacher in first_lesson.teachers.all():
                cache.delete('timetable_teachers_{0}'.format(str(teacher.id)))
            for teacher in second_lesson.teachers.all():
                cache.delete('timetable_teachers_{0}'.format(str(teacher.id)))
            for room in first_lesson.rooms.all():
                cache.delete('timetable_rooms_{0}'.format(str(room.id)))
            for room in second_lesson.rooms.all():
                cache.delete('timetable_rooms_{0}'.format(str(room.id)))
        else:
            lesson = Lesson.objects.get(id=request_data['lesson_id'])

            lesson.groups.add(current_group)

            cache = caches['default']

            for group in lesson.groups.all():
                cache.delete('timetable_groups_{0}'.format(str(group.id)))
            for teacher in lesson.teachers.all():
                cache.delete('timetable_teachers_{0}'.format(str(teacher.id)))
            for room in lesson.rooms.all():
                cache.delete('timetable_rooms_{0}'.format(str(room.id)))

        return JsonResponse({'status': 'OK'})
    else:
        pass

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

@require_http_methods(['POST'])
def auth_logout(request):
    logout(request)

    return JsonResponse({'result': 'OK'})
