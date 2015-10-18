from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from settings import domains
from data.models import Lesson, Group, Teacher, Room

base_context = {
    'domain': domains.FRONTEND_DOMAIN,
    'api_domain': domains.API_DOMAIN,
}

def index(request):
    context = {}
    context['base'] = base_context

    return render(request, 'index.html', context)

def timetable(request, type, id):
    context = {}
    context['base'] = base_context

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

    if request.user.is_authenticated():
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
