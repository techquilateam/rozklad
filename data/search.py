from django.db.models import Q
from .models import *

def search_group(str, queryset):
    return queryset.filter(name__istartswith=str)

def search_room(str, queryset):
    if '-' not in str:
        return queryset.filter(name__istartswith=str)
    else:
        left_str = str[:str.rfind('-')]
        right_str = str[str.rfind('-')+1:]

        return queryset.filter(Q(name=left_str, building__name__istartswith=right_str) | Q(name__istartswith=str))

def search_teacher(str, queryset):
    search_parts = str.split(' ')
    search_parts = [part for part in search_parts if part != '']

    if len(search_parts) > 0:
        complex_lookup = Q()
        for part in search_parts:
            complex_lookup &= Q(last_name__istartswith=part) | Q(first_name__istartswith=part) | Q(middle_name__istartswith=part)

        return queryset.filter(complex_lookup)
    else:
        return queryset.none()

def search_discipline(str, queryset):
    search_parts = str.split(' ')
    search_parts = [part for part in search_parts if part != '']

    if len(search_parts) > 0:
        complex_lookup = Q()
        for part in search_parts:
            complex_lookup &= Q(name__icontains=part) | Q(full_name__icontains=part)

        return queryset.filter(complex_lookup)
    else:
        return queryset.none()
