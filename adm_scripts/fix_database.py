#!/usr/bin/env python

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', sys.argv[1])
sys.path.insert(0, os.getcwd())
django.setup()

from data.models import *

def merge_disciplines(discipline_to, discipline_from):
    for lesson_to in Lesson.objects.filter(discipline=discipline_to):
        for teacher_to in lesson_to.teachers.all():
            if Lesson.objects.filter(number=lesson_to.number, day=lesson_to.day, week=lesson_to.week, teachers=teacher_to, discipline=discipline_from).exists():
                lesson_from = Lesson.objects.get(number=lesson_to.number, day=lesson_to.day, week=lesson_to.week, teachers=teacher_to, discipline=discipline_from)

                for group in lesson_from.groups.all():
                    lesson_to.groups.add(group)
                lesson_from.delete()

        for room_to in lesson_to.rooms.all():
            if Lesson.objects.filter(number=lesson_to.number, day=lesson_to.day, week=lesson_to.week, rooms=room_to, discipline=discipline_from).exists():
                lesson_from = Lesson.objects.get(number=lesson_to.number, day=lesson_to.day, week=lesson_to.week, rooms=room_to, discipline=discipline_from)

                for group in lesson_from.groups.all():
                    lesson_to.groups.add(group)
                lesson_from.delete()

    Lesson.objects.filter(discipline=discipline_from).update(discipline=discipline_to)
    discipline_from.delete()

for teacher_i, teacher in enumerate(Teacher.objects.all()):
    for week in range(1, 3):
        for day in range(1, 7):
            for number in range (1, 7):
                while Lesson.objects.filter(number=number, day=day, week=week, teachers=teacher).count() > 1:
                    unmerged_lessons = list(Lesson.objects.filter(number=number, day=day, week=week, teachers=teacher))
                    
                    print('Teacher {0} ({4}/{5}). Week {1}. Day {2}. Number {3}.'.format(teacher.name(), week, day, number, teacher_i, Teacher.objects.all().count()))
                    for i, unmerged_lesson in enumerate(unmerged_lessons):
                        print('  {0}. {1} ---- {2} ({3}) {{{4}}}'.format(i, unmerged_lesson.discipline.name, unmerged_lesson.discipline.full_name, ','.join([group.name for group in unmerged_lesson.groups.all()]), ','.join([room.full_name() for room in unmerged_lesson.rooms.all()])))

                    choose = input('Your choose: ')
                    print()

                    if choose[0] == 'd':
                        unmerged_lessons[int(choose[1:])].teachers.remove(teacher)
                    elif choose[0] == 'n':
                        lesson_to_i = int(choose[1:])
                        lesson_to = unmerged_lessons[lesson_to_i]
                        lessons_from = list(unmerged_lessons)
                        del lessons_from[lesson_to_i]

                        for lesson_from in lessons_from:
                            for group in lesson_from.groups.all():
                                lesson_to.groups.add(group)
                            lesson_from.delete()
                    else:
                        lesson_to_i = int(choose)
                        lesson_to = unmerged_lessons[lesson_to_i]
                        lessons_from = list(unmerged_lessons)
                        del lessons_from[lesson_to_i]

                        discipline_to = lesson_to.discipline
                        disciplines_from = [lesson.discipline for lesson in lessons_from]

                        for discipline_from in disciplines_from:
                            merge_disciplines(discipline_to, discipline_from)

for room_i, room in enumerate(Room.objects.all()):
    for week in range(1, 3):
        for day in range(1, 7):
            for number in range (1, 7):
                while Lesson.objects.filter(number=number, day=day, week=week, rooms=room).count() > 1:
                    unmerged_lessons = list(Lesson.objects.filter(number=number, day=day, week=week, rooms=room))
                    
                    print('Room {0} ({4}/{5}). Week {1}. Day {2}. Number {3}.'.format(room.full_name(), week, day, number, room_i, Room.objects.all().count()))
                    for i, unmerged_lesson in enumerate(unmerged_lessons):
                        print('  {0}. {1} ---- {2} ({3}) {{{4}}}'.format(i, unmerged_lesson.discipline.name, unmerged_lesson.discipline.full_name, ','.join([group.name for group in unmerged_lesson.groups.all()]), ','.join([teacher.name() for teacher in unmerged_lesson.teachers.all()])))

                    choose = input('Your choose: ')
                    print()

                    if choose[0] == 'd':
                        unmerged_lessons[int(choose[1:])].rooms.remove(room)
                    elif choose[0] == 'n':
                        lesson_to_i = int(choose[1:])
                        lesson_to = unmerged_lessons[lesson_to_i]
                        lessons_from = list(unmerged_lessons)
                        del lessons_from[lesson_to_i]

                        for lesson_from in lessons_from:
                            for group in lesson_from.groups.all():
                                lesson_to.groups.add(group)
                            lesson_from.delete()
                    else:
                        lesson_to_i = int(choose)
                        lesson_to = unmerged_lessons[lesson_to_i]
                        lessons_from = list(unmerged_lessons)
                        del lessons_from[lesson_to_i]

                        discipline_to = lesson_to.discipline
                        disciplines_from = [lesson.discipline for lesson in lessons_from]

                        for discipline_from in disciplines_from:
                            merge_disciplines(discipline_to, discipline_from)
