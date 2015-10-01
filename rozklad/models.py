from django.db import models

class Group(models.Model):
    OKR_CHOICES = (
        (0, 'bachelor'),
        (1, 'magister'),
        (2, 'specialist'),
    )

    TYPE_CHOICES = (
        (0, 'daily'),
        (1, 'extramural'),
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

    def __str__(self):
        return self.full_name()

    class Meta:
        unique_together = (('name', 'building'),)

class Discipline(models.Model):
    name = models.TextField()
    full_name = models.TextField()

    def __str__(self):
        return self.name

class Teacher(models.Model):
    last_name = models.TextField()
    first_name = models.TextField()
    middle_name = models.TextField()
    degree = models.TextField()

    def name(self):
        return self.last_name + ' ' + self.first_name + ' ' + self.middle_name

    def full_name(self):
        return self.degree + ' ' + self.last_name + ' ' + self.first_name + ' ' + self.middle_name

    def short_name(self):
        degree_parts = self.degree.split()
        result = ''
        for part in degree_parts:
            result += part[0:2]
            part = part[2:]
            for ch in part:
                if ch not in 'aeiouyAEIOUYауоыиэяюёеіїєАУОЫИЭЯЮЁЕІЇЄ':
                    result += ch
                else:
                    break
            result += '. '

        result += self.last_name + ' ' + self.first_name[0] + '. ' + self.middle_name[0] + '.'

        return result

    def __str__(self):
        return self.name()

class Lesson(models.Model):
    NUMBER_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
    )

    DAY_CHOICES = (
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    )

    WEEK_CHOICES = (
        (1, 'Week 1'),
        (2, 'Week 2'),
    )

    TYPE_CHOICES = (
        (0, 'lecture'),
        (1, 'practical'),
        (2, 'laboratory'),
    )

    number = models.IntegerField(choices=NUMBER_CHOICES)
    day = models.IntegerField(choices=DAY_CHOICES)
    week = models.IntegerField(choices=WEEK_CHOICES)
    type = models.IntegerField(choices=TYPE_CHOICES, null=True)
    discipline = models.ForeignKey(Discipline)
    groups = models.ManyToManyField(Group)
    teachers = models.ManyToManyField(Teacher, blank=True)
    rooms = models.ManyToManyField(Room, blank=True)

    def __str__(self):
        return self.discipline.name
