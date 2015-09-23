from rest_framework import viewsets, pagination
from .models import Group
from .serializers import GroupSerializer

class GroupViewPagination(pagination.LimitOffsetPagination):
    default_limit = 2
    max_limit = 3

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = GroupViewPagination
