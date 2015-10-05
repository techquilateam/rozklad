from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return render(request, 'index.html', {})

def group(request, id):
    return render(request, 'group.html', {})
