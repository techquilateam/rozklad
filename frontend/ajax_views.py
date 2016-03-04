import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from data.models import *
from data.search import *
from .page_cache import delete_timetable_cache

@require_http_methods(['POST'])
def edit_profile(request):
    if not request.user.is_authenticated():
        raise PermissionDenied
    if request.user.social_auth.all().count() > 0:
        raise PermissionDenied

    user_form = EditUserProfile(request.POST, instance=request.user)
    
    errors = user_form.errors
    if (not check_captcha(request.POST['g-recaptcha-response'])):
        errors['captcha'] = [_('Captcha not passed')]

    if not errors:
        user_form.save()

    return JsonResponse({'errors': user_form.errors})

max_results = 10

@require_http_methods(['GET'])
def search(request, type):
    if 'search' not in request.GET.keys() or request.GET['search'] == '':
        raise SuspiciousOperation

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

    week = request_data['week']
    day = request_data['day']
    number = request_data['number']
    another_week = True if request_data['another_week'] == 1 else False
    another_week_number = (2 if week == 1 else 1) if another_week else None

    if request_data['sender'] == 'group':
        current_group = Group.objects.get(id=request_data['id'])

        if not (request.user.has_perm('edit_group_timetable', current_group) or request.user.has_perm('data.edit_group_timetable')):
            raise PermissionDenied
        
        if ((not another_week) and Lesson.objects.filter(week=week, day=day, number=number, groups=current_group).exists()):
            raise SuspiciousOperation
        elif (another_week and Lesson.objects.filter(day=day, number=number, groups=current_group).exists()):
            raise SuspiciousOperation

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

        delete_timetable_cache('groups', current_group.id)

        return JsonResponse({'status': 'OK'})
    else:
        current_teacher = Teacher.objects.get(id=request_data['id'])

        if not (request.user.has_perm('edit_teacher_timetable', current_teacher) or request.user.has_perm('data.edit_teacher_timetable')):
            raise PermissionDenied

        if ((not another_week) and Lesson.objects.filter(week=week, day=day, number=number, teachers=current_teacher).exists()):
            raise SuspiciousOperation
        elif (another_week and Lesson.objects.filter(day=day, number=number, teachers=current_teacher).exists()):
            raise SuspiciousOperation

        discipline = Discipline.objects.get(id=request_data['discipline_id'])

        groups = [Group.objects.get(id=id) for id in request_data['groups_id']]
        if len(groups) == 0:
            raise SuspiciousOperation

        conflicts = []

        for group in groups:
            if Lesson.objects.filter(number=number, day=day, week=week, groups=group).exists():
                conflicts.append({
                    'lesson': Lesson.objects.get(number=number, day=day, week=week, groups=group),
                    'group': group,
                })

        if another_week:
            for group in groups:
                if Lesson.objects.filter(number=number, day=day, week=another_week_number, groups=group).exists():
                    conflicts.append({
                        'lesson': Lesson.objects.get(number=number, day=day, week=another_week_number, groups=group),
                        'group': group,
                    })

        if conflicts:
            if request_data['y'] == 1:
                for conflict in conflicts:
                    for group in conflict['lesson'].groups.all():
                        delete_timetable_cache('groups', group.id)
                    for teacher in conflict['lesson'].teachers.all():
                        delete_timetable_cache('teachers', teacher.id)
                    for room in conflict['lesson'].rooms.all():
                        delete_timetable_cache('rooms', room.id)

                    if conflict['lesson'].groups.all().count() == 1:
                        conflict['lesson'].delete()
                    else:
                        conflict['lesson'].groups.remove(conflict['group'])
            else:
                conflict_response = {
                    'status': 'CONFLICT',
                    'conflicts': [],
                }

                for conflict in conflicts:
                    conflict_response['conflicts'].append({
                        'type': 'group',
                        'name': conflict['group'].name,
                        'number': conflict['lesson'].number,
                        'day': conflict['lesson'].day,
                        'week': conflict['lesson'].week,
                        'teachers': [{'id': teacher.id, 'name': teacher.short_name()} for teacher in conflict['lesson'].teachers.all()],
                    })

                return JsonResponse(conflict_response)

        new_lesson = Lesson(number=number, day=day, week=week, discipline=discipline)
        new_lesson.save()
        new_lesson.teachers.add(current_teacher)
        for group in groups:
            new_lesson.groups.add(group)
        
        if another_week:
            new_lesson_2 = Lesson(number=number, day=day, week=another_week_number, discipline=discipline)
            new_lesson_2.save()
            new_lesson_2.teachers.add(current_teacher)
            for group in groups:
                new_lesson_2.groups.add(group)

        delete_timetable_cache('teachers', current_teacher.id)
        for group in groups:
            delete_timetable_cache('groups', group.id)

        return JsonResponse({'status': 'OK'})

@require_http_methods(['POST'])
def edit_lesson(request):
    request_data = json.loads(request.body.decode('utf-8'))

    current_group = Group.objects.get(id=request_data['id']) if request_data['sender'] == 'group' else None
    current_teacher = Teacher.objects.get(id=request_data['id']) if request_data['sender'] == 'teacher' else None

    if not (current_group or current_teacher):
        raise SuspiciousOperation

    current_lesson = Lesson.objects.get(id=request_data['lesson_id'])

    if current_group and (current_group not in current_lesson.groups.all()):
        raise SuspiciousOperation
    if current_teacher and (current_teacher not in current_lesson.teachers.all()):
        raise SuspiciousOperation

    if current_group and (not (request.user.has_perm('edit_group_timetable', current_group) or request.user.has_perm('data.edit_group_timetable'))):
        raise PermissionDenied
    if current_teacher and (not (request.user.has_perm('edit_teacher_timetable', current_teacher) or request.user.has_perm('data.edit_teacher_timetable'))):
        raise PermissionDenied

    type_choices_keys = [choice[0] for choice in Lesson.TYPE_CHOICES]

    current_lesson_type = None
    if request_data['lesson_type'] == 'None':
        pass
    elif int(request_data['lesson_type']) in type_choices_keys:
        current_lesson_type = int(request_data['lesson_type'])
    else:
        raise SuspiciousOperation

    conflicts = []

    old_groups_id = [group.id for group in current_lesson.groups.all()] if current_teacher else None
    old_teachers_id = [teacher.id for teacher in current_lesson.teachers.all()] if current_group else None
    old_rooms_id = [room.id for room in current_lesson.rooms.all()]
    new_groups_id = request_data['groups_id'] if current_teacher else None
    new_teachers_id = request_data['teachers_id'] if current_group else None
    new_rooms_id = request_data['rooms_id']

    if current_teacher and (len(new_groups_id) == 0):
        raise SuspiciousOperation

    add_groups_id = [id for id in new_groups_id if id not in old_groups_id] if current_teacher else None
    remove_groups_id = [id for id in old_groups_id if id not in new_groups_id] if current_teacher else None
    static_groups_id = [id for id in new_groups_id if id in old_groups_id] if current_teacher else None
    add_teachers_id = [id for id in new_teachers_id if id not in old_teachers_id] if current_group else None
    remove_teachers_id = [id for id in old_teachers_id if id not in new_teachers_id] if current_group else None
    static_teachers_id = [id for id in new_teachers_id if id in old_teachers_id] if current_group else None
    add_rooms_id = [id for id in new_rooms_id if id not in old_rooms_id]
    remove_rooms_id = [id for id in old_rooms_id if id not in new_rooms_id]
    static_rooms_id = [id for id in new_rooms_id if id in old_rooms_id]

    exclude_lesson_queryset = Lesson.objects.filter(Q(number=current_lesson.number, day=current_lesson.day, week=current_lesson.week) & ~Q(id=current_lesson.id))

    if new_groups_id:
        for group_id in new_groups_id:
            group = Group.objects.get(id=group_id)
            if exclude_lesson_queryset.filter(groups=group).exists():
                conflicts.append({
                    'type': 'group',
                    'lesson': exclude_lesson_queryset.get(groups=group),
                    'group': group,
                })

    if new_teachers_id:
        for teacher_id in new_teachers_id:
            teacher = Teacher.objects.get(id=teacher_id)
            if exclude_lesson_queryset.filter(teachers=teacher).exists():
                conflicts.append({
                    'type': 'teacher',
                    'lesson': exclude_lesson_queryset.get(teachers=teacher),
                    'teacher': teacher,
                })

    for room_id in new_rooms_id:
        room = Room.objects.get(id=room_id)
        if exclude_lesson_queryset.filter(rooms=room).exists():
            conflicts.append({
                'type': 'room',
                'lesson': exclude_lesson_queryset.get(rooms=room),
                'room': room,
            })

    another_week = True if request_data['another_week'] == 1 else False

    current_lesson_2 = None
    add_groups_id_2 = None
    remove_groups_id_2 = None
    static_groups_id_2 = None
    add_teachers_id_2 = None
    remove_teachers_id_2 = None
    static_teachers_id_2 = None
    add_rooms_id_2 = None
    remove_rooms_id_2 = None
    static_rooms_id_2 = None
    if another_week:
        another_week_number = 2 if current_lesson.week == 1 else 1

        if current_group:
            current_lesson_2 = Lesson.objects.get(number=current_lesson.number, day=current_lesson.day, week=another_week_number, discipline=current_lesson.discipline, groups=current_group)
        elif current_teacher:
            current_lesson_2 = Lesson.objects.get(number=current_lesson.number, day=current_lesson.day, week=another_week_number, discipline=current_lesson.discipline, teachers=current_teacher)

        if not current_lesson_2:
            raise SuspiciousOperation

        old_groups_id_2 = [group.id for group in current_lesson_2.groups.all()] if current_teacher else None
        old_teachers_id_2 = [teacher.id for teacher in current_lesson_2.teachers.all()] if current_group else None
        old_rooms_id_2 = [room.id for room in current_lesson_2.rooms.all()]

        add_groups_id_2 = [id for id in new_groups_id if id not in old_groups_id_2] if current_teacher else None
        remove_groups_id_2 = [id for id in old_groups_id_2 if id not in new_groups_id] if current_teacher else None
        static_groups_id_2 = [id for id in new_groups_id if id in old_groups_id_2] if current_teacher else None
        add_teachers_id_2 = [id for id in new_teachers_id if id not in old_teachers_id_2] if current_group else None
        remove_teachers_id_2 = [id for id in old_teachers_id_2 if id not in new_teachers_id] if current_group else None
        static_teachers_id_2 = [id for id in new_teachers_id if id in old_teachers_id_2] if current_group else None
        add_rooms_id_2 = [id for id in new_rooms_id if id not in old_rooms_id_2]
        remove_rooms_id_2 = [id for id in old_rooms_id_2 if id not in new_rooms_id]
        static_rooms_id_2 = [id for id in new_rooms_id if id in old_rooms_id_2]

        exclude_lesson_queryset_2 = Lesson.objects.filter(Q(number=current_lesson_2.number, day=current_lesson_2.day, week=current_lesson_2.week) & ~Q(id=current_lesson_2.id))

        if new_groups_id:
            for group_id in new_groups_id:
                group = Group.objects.get(id=group_id)
                if exclude_lesson_queryset_2.filter(groups=group).exists():
                    conflicts.append({
                        'type': 'group',
                        'lesson': exclude_lesson_queryset_2.get(groups=group),
                        'group': group,
                    })

        if new_teachers_id:
            for teacher_id in new_teachers_id:
                teacher = Teacher.objects.get(id=teacher_id)
                if exclude_lesson_queryset_2.filter(teachers=teacher).exists():
                    conflicts.append({
                        'type': 'teacher',
                        'lesson': exclude_lesson_queryset_2.get(teachers=teacher),
                        'teacher': teacher,
                    })

        for room_id in new_rooms_id:
            room = Room.objects.get(id=room_id)
            if exclude_lesson_queryset_2.filter(rooms=room).exists():
                conflicts.append({
                    'type': 'room',
                    'lesson': exclude_lesson_queryset_2.get(rooms=room),
                    'room': room,
                })

    if conflicts:
        if request_data['y'] == 1:
            for conflict in conflicts:
                for group in conflict['lesson'].groups.all():
                    delete_timetable_cache('groups', group.id)
                for teacher in conflict['lesson'].teachers.all():
                    delete_timetable_cache('teachers', teacher.id)
                for room in conflict['lesson'].rooms.all():
                    delete_timetable_cache('rooms', room.id)

                if conflict['type'] == 'group':
                    if conflict['lesson'].groups.all().count() == 1:
                        conflict['lesson'].delete()
                    else:
                        conflict['lesson'].groups.remove(conflict['group'])
                elif conflict['type'] == 'teacher':
                    conflict['lesson'].teachers.remove(conflict['teacher'])
                else:
                    conflict['lesson'].rooms.remove(conflict['room'])
        else:
            conflict_response = {
                'status': 'CONFLICT',
                'conflicts': [],
            }

            for conflict in conflicts:
                if conflict['type'] == 'group':
                    conflict_response['conflicts'].append({
                        'type': 'group',
                        'name': conflict['group'].name,
                        'number': conflict['lesson'].number,
                        'day': conflict['lesson'].day,
                        'week': conflict['lesson'].week,
                        'groups': [{'id': group.id, 'name': group.name} for group in conflict['lesson'].groups.all()],
                        'teachers': [{'id': teacher.id, 'name': teacher.short_name()} for teacher in conflict['lesson'].teachers.all()],
                    })
                elif conflict['type'] == 'teacher':
                    conflict_response['conflicts'].append({
                        'type': 'teacher',
                        'name': conflict['teacher'].name(),
                        'number': conflict['lesson'].number,
                        'day': conflict['lesson'].day,
                        'week': conflict['lesson'].week,
                        'groups': [{'id': group.id, 'name': group.name} for group in conflict['lesson'].groups.all()],
                        'teachers': [{'id': teacher.id, 'name': teacher.short_name()} for teacher in conflict['lesson'].teachers.all()],
                    })
                else:
                    conflict_response['conflicts'].append({
                        'type': 'room',
                        'name': conflict['room'].full_name(),
                        'number': conflict['lesson'].number,
                        'day': conflict['lesson'].day,
                        'week': conflict['lesson'].week,
                        'groups': [{'id': group.id, 'name': group.name} for group in conflict['lesson'].groups.all()],
                        'teachers': [{'id': teacher.id, 'name': teacher.short_name()} for teacher in conflict['lesson'].teachers.all()],
                    })

            return JsonResponse(conflict_response)

    current_lesson.type = current_lesson_type
    current_lesson.save()

    if remove_groups_id:
        for group_id in remove_groups_id:
            current_lesson.groups.remove(Group.objects.get(id=group_id))
            delete_timetable_cache('groups', group_id)
    if remove_teachers_id:
        for teacher_id in remove_teachers_id:
            current_lesson.teachers.remove(Teacher.objects.get(id=teacher_id))
            delete_timetable_cache('teachers', teacher_id)
    for room_id in remove_rooms_id:
        current_lesson.rooms.remove(Room.objects.get(id=room_id))
        delete_timetable_cache('rooms', room_id)

    if add_groups_id:
        for group_id in add_groups_id:
            current_lesson.groups.add(Group.objects.get(id=group_id))
            delete_timetable_cache('groups', group_id)
    if add_teachers_id:
        for teacher_id in add_teachers_id:
            current_lesson.teachers.add(Teacher.objects.get(id=teacher_id))
            delete_timetable_cache('teachers', teacher_id)
    for room_id in add_rooms_id:
        current_lesson.rooms.add(Room.objects.get(id=room_id))
        delete_timetable_cache('rooms', room_id)

    if static_groups_id:
        for group_id in static_groups_id:
            delete_timetable_cache('groups', group_id)
    if static_teachers_id:
        for teacher_id in static_teachers_id:
            delete_timetable_cache('teachers', teacher_id)
    for room_id in static_rooms_id:
        delete_timetable_cache('rooms', room_id)

    if current_group:
        for group in current_lesson.groups.all():
            delete_timetable_cache('groups', group.id)
    if current_teacher:
        for teacher in current_lesson.teachers.all():
            delete_timetable_cache('teachers', teacher.id)

    if another_week:
        current_lesson_2.type = current_lesson_type
        current_lesson_2.save()

        if remove_groups_id_2:
            for group_id in remove_groups_id_2:
                current_lesson_2.groups.remove(Group.objects.get(id=group_id))
                delete_timetable_cache('groups', group_id)
        if remove_teachers_id_2:
            for teacher_id in remove_teachers_id_2:
                current_lesson_2.teachers.remove(Teacher.objects.get(id=teacher_id))
                delete_timetable_cache('teachers', teacher_id)
        for room_id in remove_rooms_id_2:
            current_lesson_2.rooms.remove(Room.objects.get(id=room_id))
            delete_timetable_cache('rooms', room_id)

        if add_groups_id_2:
            for group_id in add_groups_id_2:
                current_lesson_2.groups.add(Group.objects.get(id=group_id))
                delete_timetable_cache('groups', group_id)
        if add_teachers_id_2:
            for teacher_id in add_teachers_id_2:
                current_lesson_2.teachers.add(Teacher.objects.get(id=teacher_id))
                delete_timetable_cache('teachers', teacher_id)
        for room_id in add_rooms_id_2:
            current_lesson_2.rooms.add(Room.objects.get(id=room_id))
            delete_timetable_cache('rooms', room_id)

        if static_groups_id_2:
            for group_id in static_groups_id_2:
                delete_timetable_cache('groups', group_id)
        if static_teachers_id_2:
            for teacher_id in static_teachers_id_2:
                delete_timetable_cache('teachers', teacher_id)
        for room_id in static_rooms_id_2:
            delete_timetable_cache('rooms', room_id)

        if current_group:
            for group in current_lesson_2.groups.all():
                delete_timetable_cache('groups', group.id)
        if current_teacher:
            for teacher in current_lesson_2.teachers.all():
                delete_timetable_cache('teachers', teacher.id)

    return JsonResponse({'status': 'OK'})

@require_http_methods(['POST'])
def remove_lesson(request):
    request_data = json.loads(request.body.decode('utf-8'))

    current_group = Group.objects.get(id=request_data['id']) if request_data['sender'] == 'group' else None
    current_teacher = Teacher.objects.get(id=request_data['id']) if request_data['sender'] == 'teacher' else None

    if not (current_group or current_teacher):
        raise SuspiciousOperation

    if current_group and (not (request.user.has_perm('edit_group_timetable', current_group) or request.user.has_perm('data.edit_group_timetable'))):
        raise PermissionDenied
    if current_teacher and (not (request.user.has_perm('edit_teacher_timetable', current_teacher) or request.user.has_perm('data.edit_teacher_timetable'))):
        raise PermissionDenied

    current_lesson = Lesson.objects.get(id=request_data['lesson_id'])

    if current_group and (current_group not in current_lesson.groups.all()):
        raise SuspiciousOperation
    if current_teacher and (current_teacher not in current_lesson.teachers.all()):
        raise SuspiciousOperation

    another_week = True if request_data['another_week'] == 1 else False

    current_lesson_2 = None
    if another_week:
        another_week_number = 2 if current_lesson.week == 1 else 1

        if current_group:
            current_lesson_2 = Lesson.objects.get(number=current_lesson.number, day=current_lesson.day, week=another_week_number, discipline=current_lesson.discipline, groups=current_group)
        elif current_teacher:
            current_lesson_2 = Lesson.objects.get(number=current_lesson.number, day=current_lesson.day, week=another_week_number, discipline=current_lesson.discipline, teachers=current_teacher)

        if not current_lesson_2:
            raise SuspiciousOperation

    for group in current_lesson.groups.all():
        delete_timetable_cache('groups', group.id)
    for teacher in current_lesson.teachers.all():
        delete_timetable_cache('teachers', teacher.id)
    for room in current_lesson.rooms.all():
        delete_timetable_cache('rooms', room.id)

    if current_group:
        if current_lesson.groups.all().count() == 1:
            current_lesson.delete()
        else:
            current_lesson.groups.remove(current_group)
    if current_teacher:
        current_lesson.teachers.remove(current_teacher)

    if another_week:
        for group in current_lesson_2.groups.all():
            delete_timetable_cache('groups', group.id)
        for teacher in current_lesson_2.teachers.all():
            delete_timetable_cache('teachers', teacher.id)
        for room in current_lesson_2.rooms.all():
            delete_timetable_cache('rooms', room.id)

        if current_group:
            if current_lesson_2.groups.all().count() == 1:
                current_lesson_2.delete()
            else:
                current_lesson_2.groups.remove(current_group)
        if current_teacher:
            current_lesson_2.teachers.remove(current_teacher)

    return JsonResponse({'status': 'OK'})

@require_http_methods(['POST'])
def link_lesson(request):
    request_data = json.loads(request.body.decode('utf-8'))

    if request_data['sender'] == 'group':
        current_group = Group.objects.get(id=request_data['id'])

        if not (request.user.has_perm('edit_group_timetable', current_group) or request.user.has_perm('data.edit_group_timetable')):
            raise PermissionDenied

        another_week = True if request_data['another_week'] == 1 else False

        if another_week:
            first_lesson = Lesson.objects.get(id=request_data['lesson_id'])
            second_lesson = Lesson.objects.get(id=request_data['second_lesson_id'])

            if (first_lesson.number != second_lesson.number or
                first_lesson.day != second_lesson.day or
                first_lesson.discipline != second_lesson.discipline or
                len([group for group in first_lesson.groups.all() if group in second_lesson.groups.all()]) == 0):
                raise SuspiciousOperation

            first_lesson.groups.add(current_group)
            second_lesson.groups.add(current_group)

            for group in first_lesson.groups.all():
                delete_timetable_cache('groups', group.id)
            for group in second_lesson.groups.all():
                delete_timetable_cache('groups', group.id)
            for teacher in first_lesson.teachers.all():
                delete_timetable_cache('teachers', teacher.id)
            for teacher in second_lesson.teachers.all():
                delete_timetable_cache('teachers', teacher.id)
            for room in first_lesson.rooms.all():
                delete_timetable_cache('rooms', room.id)
            for room in second_lesson.rooms.all():
                delete_timetable_cache('rooms', room.id)
        else:
            lesson = Lesson.objects.get(id=request_data['lesson_id'])

            lesson.groups.add(current_group)

            for group in lesson.groups.all():
                delete_timetable_cache('groups', group.id)
            for teacher in lesson.teachers.all():
                delete_timetable_cache('teachers', teacher.id)
            for room in lesson.rooms.all():
                delete_timetable_cache('rooms', room.id)

        return JsonResponse({'status': 'OK'})
    else:
        pass

    return JsonResponse(request_data)

@require_http_methods(['POST'])
def auth_login(request):
    if (not check_captcha(request.POST['g-recaptcha-response'])):
        return JsonResponse({'status': 'ERROR', 'error_code': 1})

    username = request.POST['username']
    password = request.POST['password']
    
    user = authenticate(username=username, password=password)

    if user:
        login(request, user)

        return JsonResponse({'status': 'OK'})
    else:
        return JsonResponse({'status': 'ERROR', 'error_code': 0})

@require_http_methods(['POST'])
def auth_logout(request):
    logout(request)

    return JsonResponse({'status': 'OK'})
