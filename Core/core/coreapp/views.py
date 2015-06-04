from django.shortcuts import render
from django.shortcuts import render_to_response
from .models import CoreUser,Project
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.http import  HttpResponse, HttpResponseRedirect
import requests
import json
import pickle
import os
import subprocess
import re


def home(request):
    """

    The view function for showing different methods of importing repositories.

    """
    with open('core/core.conf', 'r') as conf_file:
        conf = json.load(conf_file)
    client_id = conf["GITHUB_CLIENT_ID"]
    client_secret = conf["GITHUB_CLIENT_SECRET"]
    return render_to_response('index.html',{'client_id':client_id, 'client_secret':client_secret}, RequestContext(request))


def callback(request):
    """

    The function to handle the callback response of GitHub API.

    """
    code = request.META['QUERY_STRING'][5:]
    response = requests.post('https://github.com/login/oauth/access_token',params={'code':code,'client_id':'6f1b7590bb85caa50b0e','client_secret':'8d2642a02a2afa92d4308a62495cead5501b78dd'},headers={'Content-Type':'application/json','accept':'application/json'})
    if response.status_code == 200:
        login_info = response.json()
        access_token = login_info['access_token']
        # pickle.dump(login_info, open("auth_data.p", "wb"))
        user_info_url = 'https://api.github.com/user?access_token=%s'% access_token
        prof_data = requests.get(user_info_url)
        username = prof_data.json()['login']
        obj, created = CoreUser.objects.get_or_create(username=username)
        obj.user_token = access_token
        obj.save()
        response = HttpResponseRedirect( '/projects/' )
        response.set_cookie( 'core_username', username )
        return response
    else:
        return render_to_response('index.html')


def projects(request):
    """

    The view function to display all projects from the user's GitHub account

    """
    if request.COOKIES.has_key( 'core_username' ):
        # login_info = pickle.load(open("auth_data.p", "rb"))
        username = request.COOKIES['core_username']
        user = CoreUser.objects.get(username=username)
        access_token = user.user_token
        response = requests.get('https://api.github.com/user/repos?per_page=100&access_token=%s' % access_token)
        projects_list = response.json()
        projects = []
        for project_dict in projects_list:
            project, created  = Project.objects.get_or_create(project_name=project_dict['name'], core_user=user)             
            commits_url = project_dict['commits_url']
            commits_url = re.sub('\{/sha}$', '', commits_url)
            project.commits_url = commits_url
            project.clone_url = project_dict['clone_url']
            project.repo_url = project_dict['url']
            project.private = project_dict['private']
            if created == True:
                project.save()           
            projects.append(project)
        response = render_to_response('Projects.html',{'projects_list':projects}, RequestContext(request))
        print projects
        return response
    else:
        render_to_response('index.html')


def sources(request):
    return render_to_response('sources.html')

@csrf_exempt
def demo(request):
    repo_name = request.POST.get('repo_name')
    clone_url = request.POST.get('clone_url')
    private = request.POST.get('private')
    if private == "True":
        project_type = "Private"
    elif private == "False":
        project_type = "Public"
    path = '{}/github/user/repos/{}'.format(os.getcwd(),repo_name)
    url = "git clone {} {}".format(clone_url,path)
    os.system("git clone {} {}".format(clone_url,path))
    # try:
    #     subprocess.call("git clone {} {}".format(clone_url,path))
    # except OSError:
    #     print('Directory already exists')

    return render_to_response('test.html',{'repo_name':repo_name,'clone_url':clone_url,'project_type':project_type})
