from django.contrib import admin
from .models import CoreUser, Project

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'date_joined', 'is_staff')
    search_fields = ['username']
    fieldsets = [
    ('User Details', {'fields': [('username', 'user_token')]}),
    ('Account Status', {'fields': ['is_superuser', 'is_staff', 'is_active'], 'classes': ('collapse',)}),
    (None, {'fields': [ 'date_joined']}),
    ]
    inlines = [ProjectInline]   

admin.site.register(CoreUser, UserAdmin)
admin.site.register(Project)