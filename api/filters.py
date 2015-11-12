from rest_framework import filters
from data.models import *
from data.search import *

class SearchGroupFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if 'search' not in request.GET.keys():
            return queryset
        else:
            return search_group(request.GET['search'], queryset)

class SearchRoomFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if 'search' not in request.GET.keys():
            return queryset
        else:
            return search_room(request.GET['search'], queryset)

class SearchTeacherFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if 'search' not in request.GET.keys():
            return queryset
        else:
            return search_teacher(request.GET['search'], queryset)

class SearchDisciplineFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if 'search' not in request.GET.keys():
            return queryset
        else:
            return search_discipline(request.GET['search'], queryset)
