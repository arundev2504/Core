from django.shortcuts import render
from django.shortcuts import render_to_response
from .models import CoreUser,Project
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from os.path import expanduser
import requests
import json
import pickle
import os
import subprocess

# Create your views here.
def home(request):
    return render_to_response('index.html')


def callback(request):
    code = request.META['QUERY_STRING'][5:]
    print('code is : ' + code)
    response = requests.post('https://github.com/login/oauth/access_token',params={'code':code,'client_id':'6f1b7590bb85caa50b0e','client_secret':'8d2642a02a2afa92d4308a62495cead5501b78dd'},headers={'Content-Type':'application/json','accept':'application/json'})
    if response.status_code == 200:
        login_info = response.json()
        print('access token here.....')
        print(login_info)
        pickle.dump(login_info, open("auth_data.p", "wb"))
        user_info_url = 'https://api.github.com/user?access_token=%s'% login_info['access_token']
        prof_data = requests.get(user_info_url)
        if prof_data.status_code == 200:
            # print('Here is the prof info')
            # print(prof_data.json())
            response = requests.get('https://api.github.com/user/repos?per_page=100&access_token=%s' % login_info['access_token'])
            projects_list = response.json()
            projects = []
            for project_dict in projects_list:
                # print(project_dict)
                project = Project.objects.create()
                project.project_name = project_dict['name']
                project.clone_url = project_dict['clone_url']
                project.repo_url = project_dict['url']
                projects.append(project)
            return render_to_response('projects.html',{'projects_list':projects}, context_instance=RequestContext(request))
            # return render_to_response('Callback.html')
        return render_to_response('index.html')
    return render_to_response('index.html')


def projects(request):
    login_info = pickle.load(open("auth_data.p", "rb"))
    print(login_info)
    response = requests.get('https://api.github.com/user/repos?per_page=100&access_token=%s' % login_info['access_token'])
    projects_list = response.json()
    projects = []
    for project_dict in projects_list:
        project = Project.objects.create()
        project.project_name = project_dict['name']
        project.clone_url = project_dict['clone_url']
        project.repo_url = project_dict['url']
        projects.append(project)
    return render_to_response('projects.html',{'projects_list':projects}, context_instance=RequestContext(request))


def sources(request):
    return render_to_response('sources.html')

@csrf_exempt
def demo(request):
    repo_name = request.POST.get('repo_name')
    clone_url = request.POST.get('clone_url')
    home = expanduser("~")
    path = '{}/core_app/github/user/repos/{}'.format(home,repo_name)
    url = "git clone {} {}".format(clone_url,path)
    os.system("git clone {} {}".format(clone_url,path))
    # try:
    #     subprocess.call("git clone {} {}".format(clone_url,path))
    # except OSError:
    #     print('Directory already exists')

    return render_to_response('test.html',{'repo_name':repo_name,'clone_url':clone_url})

#   Create user object
def create_user(user_data):
    username = user_data['username']
    user = CoreUser.objects.get_or_create(user_data['username'])
