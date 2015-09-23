from rest_framework import serializers
from .models import Group, Building, Room

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'okr', 'type')

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ('id', 'number', 'latitude', 'longitude')

class RoomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Room
        fields = ('id', 'name', 'full_name', 'building')
