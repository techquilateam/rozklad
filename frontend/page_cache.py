from django.core.cache import caches
from django.core.cache.utils import make_template_fragment_key

cache = caches['default']

def get_timetable_cache(type, id):
    id = int(id)
    cache_key = make_template_fragment_key('timetable', [type, id])
    return cache.get(cache_key)

def delete_timetable_cache(type, id):
    id = int(id)
    cache_key = make_template_fragment_key('timetable', [type, id])
    cache.delete(cache_key)
