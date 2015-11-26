from django.contrib import admin
from django.contrib.auth.models import User
from django.conf.urls import url
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect
from social.apps.django_app.default.models import UserSocialAuth
from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import assign_perm
from data.models import Building, Room, Group, Teacher, Discipline, Lesson
from .models import UnregisteredVKUserTimetablePermissions
from .forms import AddVKUserPermissions

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'building')
    list_filter = ('building',)
    search_fields = ('^name',)

@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_name')
    search_fields = ('name', 'full_name')

@admin.register(Group)
class GroupAdmin(GuardedModelAdmin):
    list_display = ('name', 'okr', 'type')
    list_filter = ('okr', 'type')
    search_fields = ('^name',)

@admin.register(Teacher)
class TeacherAdmin(GuardedModelAdmin):
    list_display = ('name', 'last_name', 'first_name', 'middle_name', 'degree', 'full_name', 'short_name')
    search_fields = ('^last_name', '^first_name', '^middle_name')

@admin.register(UnregisteredVKUserTimetablePermissions)
class UnregisteredVKUserTimetablePermissionsAdmin(admin.ModelAdmin):
    list_display = ('vk_user_id', 'groups_str', 'teachers_str')
    filter_horizontal = ('groups', 'teachers')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'vk-perms/$', self.admin_site.admin_view(self.vk_perms)),
        ]
        return my_urls + urls

    def vk_perms(self, request):
        context = self.admin_site.each_context(request)

        if request.method == 'GET':
            context['form'] = AddVKUserPermissions()
            return TemplateResponse(request, 'vk_perms.html', context)
        else:
            form = AddVKUserPermissions(request.POST)
            
            if form.errors:
                context['form'] = form
                context['errors'] = True
                return TemplateResponse(request, 'vk_perms.html', context)
            else:
                form_data = form.clean()

                if UserSocialAuth.objects.filter(uid=form_data['identifier']).exists():
                    user = UserSocialAuth.objects.get(uid=form_data['identifier']).user

                    for group in form_data['groups']:
                        assign_perm('edit_group_timetable', user, group)
                    for teacher in form_data['teachers']:
                        assign_perm('edit_teacher_timetable', user, teacher)
                else:
                    perms = UnregisteredVKUserTimetablePermissions(vk_user_id=int(form_data['identifier']))
                    perms.save()

                    for group in form_data['groups']:
                        perms.groups.add(group)
                    for teacher in form_data['teachers']:
                        perms.teachers.add(teacher)

                if '_addanother' in request.POST:
                    return HttpResponseRedirect('/admin/frontend/unregisteredvkusertimetablepermissions/vk-perms/')
                else:
                    return HttpResponseRedirect('/admin/frontend/unregisteredvkusertimetablepermissions/')
