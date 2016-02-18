#!/usr/bin/env python

import json
import socket
import urllib.parse
import os
import sys
import django
from collections import OrderedDict
from http.client import HTTPConnection
from bs4 import BeautifulSoup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', sys.argv[1])
sys.path.insert(0, os.getcwd())
django.setup()

from data.models import *

socket.setdefaulttimeout(1)

def process_request(host, method, url, body=None, headers={}):
    while True:
        try:
            conn = HTTPConnection(host)
            conn.request(method, url, body, headers)
            return conn.getresponse()
        except (socket.timeout, socket.gaierror):
            pass

def normal_group_name(group_name):
    return group_name.lower().replace(' ', '')

ukr_alphabet = 'абвгґдеєжзиіїйклмнопрстуфхцчшщьюя'

print('Step 1 (collect group uuids)')
group_uuids = None

group_strings = []

for ch in ukr_alphabet:
    response = process_request('rozklad.kpi.ua', 'POST', '/Schedules/ScheduleGroupSelection.aspx/GetGroups', '{{"prefixText":"{0}","count":10}}'.format(ch).encode(), {'Content-Type': 'application/json; charset=UTF-8'})
    response = json.loads(response.read().decode('utf-8'))['d']
    if response is not None:
        for group in response:
            group_strings.append(group)

group_uuids = OrderedDict()

for group in group_strings:
    post_data = {
        '__EVENTVALIDATION': '/wEdAAEAAAD/////AQAAAAAAAAAPAQAAAAUAAAAIsA3rWl3AM+6E94I5Tu9cRJoVjv0LAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHfLZVQO6kVoZVPGurJN4JJIAuaU',
        '__VIEWSTATE': '/wEMDAwQAgAADgEMBQAMEAIAAA4BDAUDDBACAAAOAgwFBwwQAgwPAgEIQ3NzQ2xhc3MBD2J0biBidG4tcHJpbWFyeQEEXyFTQgUCAAAADAUNDBACAAAOAQwFAQwQAgAADgEMBQsMEAIMDwEBBFRleHQBG9Cg0L7Qt9C60LvQsNC0INC30LDQvdGP0YLRjAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHSLgM7jte8qEzke6Y92dcYT7p/X',
        'ctl00$MainContent$ctl00$btnShowSchedule': 'Розклад занять',
        'ctl00$MainContent$ctl00$txtboxGroup': group,
    }

    response = process_request('rozklad.kpi.ua', 'POST', '/Schedules/ScheduleGroupSelection.aspx', urllib.parse.urlencode(post_data).encode(), {'Content-Type': 'application/x-www-form-urlencoded'})
    location_header = response.getheader('Location')

    if location_header is not None:
        group_uuids[normal_group_name(group)] = urllib.parse.parse_qs(urllib.parse.urlparse(location_header).query)['g'][0]
    else:
        soup = BeautifulSoup(response.read().decode('utf-8'), 'html.parser')

        for a_tag in soup.find(id='ctl00_MainContent_ctl00_GroupListPanel').find_all('a'):
            group_uuids[normal_group_name(a_tag.next)] = urllib.parse.parse_qs(urllib.parse.urlparse(a_tag['href']).query)['g'][0]

print('Step 1 (collect group uuids) passed')

print('Step 2 (main phase)')

for i, (group_name, group_uuid) in enumerate(group_uuids.items()):
    print('{0} ({1}/{2})'.format(group_name, i, len(group_uuids)))

    clean_group_name = group_name
    if '(' in clean_group_name:
        clean_group_name = clean_group_name[:clean_group_name.find('(')]

    group_okr = 0
    if clean_group_name[-1] == 'м':
        group_okr = 1
    elif clean_group_name[-1] == 'с':
        group_okr = 2

    group_type = 0
    if clean_group_name[clean_group_name.find('-') + 1] == 'з':
        group_type = 1

    group = Group(name=group_name, okr=group_okr, type=group_type)
    group.save()

    response = process_request('rozklad.kpi.ua', 'GET', '/Schedules/ViewSchedule.aspx?g={0}'.format(group_uuid))
    soup = BeautifulSoup(response.read().decode('utf-8'), 'html.parser')

    tables = [soup.find(id='ctl00_MainContent_FirstScheduleTable'), soup.find(id='ctl00_MainContent_SecondScheduleTable')]
    for table_i, table in enumerate(tables):
        tr_tags = table.find_all('tr')[1:]
        for tr_tag_i, tr_tag in enumerate(tr_tags):
            td_tags = tr_tag.find_all('td')[1:]
            for td_tag_i, td_tag in enumerate(td_tags):
                lesson_week = table_i + 1
                lesson_day = td_tag_i + 1
                lesson_number = tr_tag_i + 1

                a_tags = td_tag.find_all('a')
                if a_tags:
                    discipline_a_tag = a_tags[0]

                    discipline = None
                    if Discipline.objects.filter(full_name=discipline_a_tag['title']).exists():
                        discipline = Discipline.objects.get(full_name=discipline_a_tag['title'])
                    else:
                        discipline = Discipline(name=discipline_a_tag.next, full_name=discipline_a_tag['title'])
                        discipline.save()

                    teachers = []
                    rooms = []
                    lesson_type = None

                    for a_tag in a_tags:
                        if a_tag['href'].find('/Schedules/ViewSchedule.aspx') != -1:
                            teacher_str_list = a_tag['title'].split(' ')
                            
                            teacher_middle_name = teacher_str_list[-1].lower()
                            if len(teacher_middle_name) > 0:
                                teacher_middle_name = teacher_middle_name[0].upper() + teacher_middle_name[1:]
                            teacher_first_name = teacher_str_list[-2].lower()
                            if len(teacher_first_name) > 0:
                                teacher_first_name = teacher_first_name[0].upper() + teacher_first_name[1:]
                            teacher_last_name = teacher_str_list[-3].lower()
                            if len(teacher_last_name) > 0:
                                teacher_last_name = teacher_last_name[0].upper() + teacher_last_name[1:]
                            teacher_degree = ''
                            if teacher_str_list[:-3]:
                                teacher_degree = ' '.join(teacher_str_list[:-3]).lower()

                            teacher = None
                            if Teacher.objects.filter(last_name=teacher_last_name, first_name=teacher_first_name, middle_name=teacher_middle_name).exists():
                                teacher = Teacher.objects.get(last_name=teacher_last_name, first_name=teacher_first_name, middle_name=teacher_middle_name)
                            else:
                                teacher = Teacher(last_name=teacher_last_name, first_name=teacher_first_name, middle_name=teacher_middle_name, degree=teacher_degree)
                                teacher.save()

                            teachers.append(teacher)
                        elif a_tag['href'].find('maps.google.com') != -1:
                            room_full_str = a_tag.next
                            
                            room_str = None
                            lesson_type_str = None
                            if ' ' in room_full_str:
                                room_str = room_full_str[:room_full_str.find(' ')]
                                lesson_type_str = room_full_str[room_full_str.rfind(' ') + 1:]
                            else:
                                room_str = room_full_str
                                lesson_type_str = room_full_str

                            if lesson_type_str == 'Лек':
                                lesson_type = 0
                            elif lesson_type_str == 'Прак':
                                lesson_type = 1
                            elif lesson_type_str == 'Лаб':
                                lesson_type = 2

                            if '-' in room_str:
                                room_name = room_str[:room_str.rfind('-')]
                                building_name = room_str[room_str.rfind('-') + 1:]

                                if building_name.isdigit():
                                    building_name = str(int(building_name))

                                building = None
                                if Building.objects.filter(name=building_name).exists():
                                    building = Building.objects.get(name=building_name)
                                else:
                                    building_latitude = urllib.parse.parse_qs(urllib.parse.urlparse(a_tag['href']).query)['q'][0].split(',')[0]
                                    building_longitude = urllib.parse.parse_qs(urllib.parse.urlparse(a_tag['href']).query)['q'][0].split(',')[1]

                                    building = Building(name=building_name, latitude=building_latitude, longitude=building_longitude)
                                    building.save()

                                room = None
                                if Room.objects.filter(name=room_name, building=building).exists():
                                    room = Room.objects.get(name=room_name, building=building)
                                else:
                                    room = Room(name=room_name, building=building)
                                    room.save()

                                rooms.append(room)

                    lesson = None
                    for teacher in teachers:
                        if Lesson.objects.filter(number=lesson_number, day=lesson_day, week=lesson_week, discipline=discipline, teachers=teacher).exists():
                            lesson = Lesson.objects.get(number=lesson_number, day=lesson_day, week=lesson_week, discipline=discipline, teachers=teacher)
                            break
                    if lesson is None:
                        for room in rooms:
                            if Lesson.objects.filter(number=lesson_number, day=lesson_day, week=lesson_week, discipline=discipline, rooms=room).exists():
                                lesson = Lesson.objects.get(number=lesson_number, day=lesson_day, week=lesson_week, discipline=discipline, rooms=room)
                                break

                    if lesson is None:
                        lesson = Lesson(number=lesson_number, day=lesson_day, week=lesson_week, discipline=discipline)
                        lesson.save()

                    lesson.type = lesson_type
                    lesson.save()

                    lesson.groups.add(group)
                    for teacher in teachers:
                        lesson.teachers.add(teacher)
                    for room in rooms:
                        lesson.rooms.add(room)
