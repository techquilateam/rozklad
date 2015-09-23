from django.db import models

class Group(models.Model):
    OKR_CHOICES = (
        (0, "bachelor"),
        (1, "magister"),
        (2, "specialist"),
    )

    TYPE_CHOICES = (
        (0, "daily"),
        (1, "extramural"),
    )

    name = models.CharField(max_length=20, unique=True)
    okr = models.IntegerField(choices=OKR_CHOICES)
    type = models.IntegerField(choices=TYPE_CHOICES)

    def __str__(self):
        return self.name

class Building(models.Model):
    number = models.IntegerField(unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return str(self.number)

class Room(models.Model):
    name = models.CharField(max_length=10)
    building = models.ForeignKey(Building)

    def full_name(self):
        return self.name + '-' + str(self.building.number)

    class Meta:
        unique_together = (('name', 'building'))
