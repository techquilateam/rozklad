from django.http import HttpResponse
from django.shortcuts import render
from rozklad import domains

base_context = {
    'domain': domains.FRONTEND_DOMAIN,
    'api_domain': domains.API_DOMAIN,
}

def index(request):
    context = {}
    context['base'] = base_context

    return render(request, 'index.html', context)

def timetable(request, id, type):
    context = {}
    context['base'] = base_context

    context['id'] = id
    context['type'] = type

    return render(request, 'timetable.html', context)
