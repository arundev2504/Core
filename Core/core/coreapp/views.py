from django.shortcuts import render
from django.shortcuts import render_to_response
from .models import CoreUser,Project
from django.template import RequestContext
from .forms import LoginForm, SignupForm
from django.views.decorators.csrf import csrf_exempt
from django.http import  HttpResponse, HttpResponseRedirect
from os.path import expanduser
from django.core.files import File
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
import requests
import json
import os
import subprocess
import re
import linecache
import datetime
import hashlib

def login(request):
    """

        The view function for login.

    """

    user = is_loggedin(request)
    if user:
        return HttpResponseRedirect('/projectlist/')
    else:
        with open('core/core.conf', 'r') as conf_file:
            conf = json.load(conf_file)
        client_id = conf["GITHUB_CLIENT_ID"]
        client_secret = conf["GITHUB_CLIENT_SECRET"] 
        return render_to_response('login.html',{'client_id':client_id, 'client_secret':client_secret}, RequestContext(request))


def signup(request):
    context = RequestContext(request)
    if request.method == 'POST' and 'signup' in request.POST:
        signup_form = SignupForm(request.POST)
        if not signup_form.is_valid():
            return render_to_response('signup.html', {'signup_form' : signup_form}, context)
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        hashed_password = make_password(password)
        CoreUser.objects.create(username=username, password=hashed_password, email=email)
        return render_to_response('manual_login.html', {'login_form' : LoginForm(initial={'username':username})}, context)
    return render_to_response('signup.html', {'signup_form' : SignupForm()}, context)

def manual_login(request):
    context = RequestContext(request)
    if request.method == 'POST' and 'login' in request.POST:
        login_form = LoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = CoreUser.objects.get(username=username)
        except CoreUser.DoesNotExist:
            messages.info(request, 'Invalid user credentials')
            return render_to_response('manual_login.html', {'login_form' : login_form}, context) 
        if not check_password(password, user.password):
            messages.info(request, 'Invalid user credentials')
            return render_to_response('manual_login.html', {'login_form' : login_form}, context)
        response = HttpResponseRedirect('/projectlist/')
        now = datetime.datetime.now()
        token = make_password(username+str(now))
        user.user_token = token
        user.save()
        response.set_cookie('core_username', username)
        response.set_cookie('token', token)
        return response
    return render_to_response('manual_login.html', {'login_form' : LoginForm()}, context)


def callback(request):
    """

        The function to handle the callback response of GitHub API.

    """

    code = request.META['QUERY_STRING'][5:]
    response = requests.post('https://github.com/login/oauth/access_token',params={'code':code,'client_id':'6f1b7590bb85caa50b0e','client_secret':'8d2642a02a2afa92d4308a62495cead5501b78dd'},headers={'Content-Type':'application/json','accept':'application/json'})
    if response.status_code == 200:
        login_info = response.json()
        access_token = login_info['access_token']
        user_info_url = 'https://api.github.com/user?access_token=%s'% access_token
        prof_data = requests.get(user_info_url)
        user = is_loggedin(request)

        # if the user has logged in manually
        if user:
            user.github_token = access_token 
            user.save()
            return HttpResponseRedirect('/projects/new/github/')

        # if the user logged in through GitHub
        else:
            username = prof_data.json()['login']
            user_obj, created = CoreUser.objects.get_or_create(username=username)
            user_obj.user_token = access_token
            user_obj.github_token = access_token 
            user_obj.save()
            response = HttpResponseRedirect('/projectlist/')
            response.set_cookie('core_username', username)
            response.set_cookie('token', access_token)
            return response     
    else:
        return HttpResponseRedirect('/login/')


def projects_github(request):
    """

        The view function to display all projects from the user's GitHub account

    """

    user = is_loggedin(request)
    if user:

        # if user is not authorized to access GitHub API 
        if not user.github_token:
            with open('core/core.conf', 'r') as conf_file:
                conf = json.load(conf_file)
            client_id = conf["GITHUB_CLIENT_ID"]
            client_secret = conf["GITHUB_CLIENT_SECRET"] 
            return HttpResponseRedirect('https://github.com/login/oauth/authorize?scope=user:email&client_id='+client_id+'&client_secret='+client_secret)
        
        # if user already logged in through GitHub
        else:
            access_token = user.github_token
            response = requests.get('https://api.github.com/user/repos?per_page=100&access_token=%s' % access_token)
            projects_list = response.json()
            projects = []
            for project_dict in projects_list:
                try:
                    project = Project.objects.get(project_name=project_dict['name'], core_user=user)
                except Project.DoesNotExist:
                    project = Project(project_name=project_dict['name'])
                    commits_url = project_dict['commits_url']
                    commits_url = re.sub('\{/sha}$', '', commits_url)
                    project.commits_url = commits_url
                    project.clone_url = project_dict['clone_url']
                    project.repo_url = project_dict['url']
                    project.private = project_dict['private']
                    project.language = project_dict['language'].lower()
                    project.save()
                    project.core_user.add(user)
                if project.project_path == None:           
                    projects.append(project)
            return render_to_response('Projects.html',{'projects_list':projects, 'username':user.username}, RequestContext(request))
    else:
        return HttpResponseRedirect('/login/')


@csrf_exempt
def clone_projects(request):
    user = is_loggedin(request)
    if user:
        repo_name = request.POST.get('repo_name')
        clone_url = request.POST.get('clone_url')
        project_id = request.POST.get('project_id')
        home = expanduser("~")
        path = '{}/core_app/github/{}/repos/{}'.format(home, user.username, repo_name)
        url = "git clone {} {}".format(clone_url,path)
        os.system("git clone {} {}".format(clone_url,path))
        project = Project.objects.get(id=project_id)
        project.project_path = path
        project.save()
        f = open(path+'/sonar-project.properties', 'w')
        myfile = File(f)
        myfile.write('sonar.language='+ project.language+'\nsonar.projectVersion=1.0\nsonar.sources=src\nsonar.sourceEncoding=UTF-8\nsonar.projectKey=' + project.project_name + '\nsonar.projectName=' + project.project_name  )
        myfile.closed
        f.closed
        p = subprocess.Popen(["sonar-runner"], cwd=path)
        return HttpResponseRedirect('/projectlist/')
    else:
        return HttpResponseRedirect('/login/')


def new_project(request):
    """

        The view function to add a new project.

    """

    user = is_loggedin(request)
    if user:
        return render_to_response('index.html', {'username':user.username})
    else:
        return HttpResponseRedirect('/login/')


def project_list(request):
    """

        The view function to show the list of projects already cloned by our application.

    """

    user = is_loggedin(request)
    if user:
        username = user.username
        projects = Project.objects.filter(core_user=user).exclude(project_path=None)
        p = []
        for project in projects:
            try:
                response = requests.get('http://localhost:9000/sonar/api/issues/search?componentKeys=%s' % project.project_name)
            except:
                return HttpResponse("Sonar connection problem")
            issues_list = response.json()
            project.issues = issues_list['total']
            p.append(project)
        if projects:
            return render_to_response('project_list.html',{'projects':p, 'username':username})
        else:
            return HttpResponseRedirect('/projects/new/')
    else:
        return HttpResponseRedirect('/login/')


def issues(request, project_id):
    """
    
        The view function to list the issues of a project.

    """

    user = is_loggedin(request)
    if user:
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return HttpResponse("You are not authorized to view this project details")
        if user in project.core_user.all():
            project_name = project.project_name
            response = requests.get('http://localhost:9000/sonar/api/issues/search?componentKeys=%s' % project_name)
            response_json = response.json()
            issues_list = response_json['issues']
            file_names = []
            component_list = response_json['components']
            for component in component_list:
                if 'path' in component.keys():
                    file_names.append(component['longName'])
            return render_to_response('issues.html',{'project_name':project_name,'issues':issues_list,'file_names':file_names,'username':user.username})
        else:
            return HttpResponse("You are not authorized to view this project details")
    else:
        return HttpResponseRedirect('/login/') 


def logout(request):
    """ 

        The function to log out an user.

    """

    user = is_loggedin(request)
    if user:
        user.user_token = ''
        user.github_token = ''
        user.save()
        response = HttpResponseRedirect('/login/')
        response.delete_cookie('core_username')
        response.delete_cookie('token')
        return response
    else:
        return HttpResponseRedirect('/login/')


def is_loggedin(request):
    """

        The function to check whether any user is logged in, if any, returns the user object.

    """

    if request.COOKIES.has_key('core_username') and request.COOKIES.has_key('token'):
        username = request.COOKIES['core_username']
        token = request.COOKIES['token']
        user = CoreUser.objects.get(username=username)
        if user.user_token == token:
            return user
        else:
            return None
    else:
        return None
    

@csrf_exempt
def get_issues_json(request):
    """

    The function to get the total number of issues for each project of a particular user in JSON format.

    """

    user = is_loggedin(request)
    if user and request.method == 'GET' and request.is_ajax():
        username = user.username
        projects_list = Project.objects.filter(core_user__username=username).exclude(project_path=None)
        issue_details = []
        for project in projects_list:
            response = requests.get('http://localhost:9000/sonar/api/issues/search?componentKeys=%s' % project.project_name)
            response_json = response.json()
            projects = response_json['projects']
            if projects:
                issues_total = response_json['total']
                projects_name = projects[0]['name']
                msg = {'issues_no': issues_total,'projects_name': projects_name}
                issue_details.append(msg)
        return HttpResponse(json.dumps(issue_details), content_type="application/json")



@csrf_exempt
def get_issues_code(request):
    """

    The function to get the code of each issue along with its key in JSON format.

    """
    user = is_loggedin(request)
    if user and request.method == 'POST' and request.is_ajax():
        project_name = request.POST.get('project_name')
        response = requests.get('http://localhost:9000/sonar/api/issues/search?componentKeys=%s' %project_name)
        response_json = response.json()
        issues_list = response_json['issues']
        if not issues_list:
            return HttpResponse("fail", content_type="application/json")
        issue_code_details = []
        for issue in issues_list:
            if 'line' in issue.keys():
                key = issue['key']
                line_no = issue['line']
                project_path = Project.objects.get(project_name=project_name, core_user=user).project_path
                component_path = issue['component']
                file_path = re.sub(project_name+':', project_path+'/', component_path)
                if line_no == 1:
                    start_limit = 1
                    end_limit = 3
                else:
                    start_limit = line_no - 1
                    end_limit = line_no + 1
                code = ''
                for i in range(start_limit,end_limit+1):
                    text = linecache.getline(file_path, i)
                    if i == line_no:
                        code = code +'%s: ' %i +'<font color=red>' +text+'</font>'
                    else:
                        code = code +'%s: ' %i +text
                issue_detail = {'key':key, 'code':code}
                issue_code_details.append(issue_detail)
        return HttpResponse(json.dumps(issue_code_details), content_type="application/json")


@csrf_exempt
def get_user_list(request):
    if request.is_ajax():
        user = is_loggedin(request)
        q = request.GET.get('term', '')
        users = CoreUser.objects.filter(username__icontains = q ).exclude(username=user.username)[:20]
        results = []
        for user in users:
            user_json = {}
            user_json['id'] = user.id
            user_json['value'] = user.username
            results.append(user_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def share_project(request):
    if request.method == 'POST' and request.is_ajax():
        project_id = request.POST.get('project_id')
        shared_with = request.POST.get('shared_with')
        project = Project.objects.get(id=project_id)
        shared_user = CoreUser.objects.get(username=shared_with)
        if project.core_user.filter(username=shared_with).exists():
            result = 'User already exists'
            data = json.dumps(result)
            return HttpResponse(data, content_type="application/json")
        project.core_user.add(shared_user)
        result = 'Success'
        data = json.dumps(result)
        return HttpResponse(data, content_type="application/json")