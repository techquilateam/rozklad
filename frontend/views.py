from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from rozklad import domains

base_context = {
    'domain': domains.FRONTEND_DOMAIN,
    'api_domain': domains.API_DOMAIN,
}

def index(request):
    context = {}
    context['base'] = base_context
    context['user'] = request.user

    return render(request, 'index.html', context)

def timetable(request, id, type):
    context = {}
    context['base'] = base_context
    context['user'] = request.user

    context['id'] = id
    context['type'] = type

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
