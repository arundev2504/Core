from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CoreUser, Project


class ProjectInline(admin.TabularInline):
    model = Project.core_user.through
    extra = 1  

class CoreUserAdmin(UserAdmin):
    list_display = ('username', 'date_joined', 'is_staff')
    search_fields = ['username']
    # fieldsets = UserAdmin.fieldsets
    fieldsets = [
    ('User Details', {'fields': [('username', 'password'),'email']}),
    ('User Tokens', {'fields': [('user_token', 'github_token')]}),
    ('Account Status', {'fields': ['is_superuser', 'is_staff', 'is_active'], 'classes': ('collapse',)}),
    (None, {'fields': [ 'date_joined']}),
    ]
    inlines = [ProjectInline] 

admin.site.register(CoreUser, CoreUserAdmin)
admin.site.register(Project)