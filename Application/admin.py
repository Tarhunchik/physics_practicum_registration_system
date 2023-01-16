from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, SchedulingSystem, DateChanger, TimeInterval


class AccountAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'grade', 'is_teacher')
    search_fields = ('first_name', 'last_name', 'username', 'email')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ('last_name',)
    fieldsets = ()


class SchedulingSystemAdmin(admin.ModelAdmin):
    list_display = ('holder', 'holder_name', 'user', 'task', 'day', 'time')
    search_fields = ('holder', 'holder_name', 'task', 'day', 'time')
    readonly_fields = ('user',)

    filter_horizontal = ()
    list_filter = ('day', 'time', 'task')
    fieldsets = ()


class DateChangerAdmin(admin.ModelAdmin):
    list_display = ('day', 'available_time')
    search_fields = ('day',)

    filter_horizontal = ()
    list_filter = ('day',)
    fieldsets = ()


class TimeIntervalsAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time')
    search_fields = ('start_time', 'end_time')

    filter_horizontal = ()
    list_filter = ('start_time', 'end_time')
    fieldsets = ()


admin.site.register(User, AccountAdmin)
admin.site.register(SchedulingSystem, SchedulingSystemAdmin)
admin.site.register(DateChanger, DateChangerAdmin)
admin.site.register(TimeInterval, TimeIntervalsAdmin)
