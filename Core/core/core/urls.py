"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from coreapp import views
import os

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', views.login, name = 'login'),
    url(r'^logout/$', views.logout, name = 'logout'),
    url(r'^callback', views.callback, name = 'callback'),
    url(r'^projectlist/$', views.project_list, name = 'projectlist'),
    url(r'^projectlist/issues/(?P<project_id>\d+)/', views.issues, name = 'issues'),
    url(r'^projects/new/github/$', views.projects, name = 'projects'),
    url(r'^projects/new/$', views.new_project, name = 'new_project'),
    url(r'^projects/clone/$', views.clone_projects, name = 'clone_projects'),
    url(r'^issues_json/$', views.get_issues_json, name = 'issues_json'),
    url(r'^issues_code/$', views.get_issues_code, name = 'issues_code'),
    url(r'^', views.login, name = 'index'),
]

site_media = os.path.join(
    os.path.dirname(__file__), 'site_media'
)

admin.site.site_header = 'CORE Administration'
admin.site.site_title = 'CORE Admin'
admin.site.index_title = 'CORE App'
admin.site.site_url = '/login/'