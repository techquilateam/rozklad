from django.db import models

class Group(models.Model):
    OKR_CHOICES = (
        (0,"bachelor"),
        (1,"magister"),
        (2,"specialist"),
    )

    TYPE_CHOICES = (
        (0,"daily"),
        (1,"extramural"),
    )

    name = models.CharField(max_length=20)
    okr = models.IntegerField(choices=OKR_CHOICES)
    type = models.IntegerField(choices=TYPE_CHOICES)
