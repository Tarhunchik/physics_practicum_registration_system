from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, SchedulingSystem


class AccountAdmin(UserAdmin):
    list_display = ('first_name', 'last_name', 'date_joined', 'last_login')
    search_fields = ('first_name', 'last_name', 'username', 'email')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(User, AccountAdmin)
admin.site.register(SchedulingSystem)
