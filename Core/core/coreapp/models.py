from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import signals
from django.conf import settings
from django.core.mail import send_mail


class CoreUser(AbstractUser):
    user_token = models.CharField(max_length=200, blank = True, null = True)
    github_token = models.CharField(max_length=200, blank = True, null = True)
    user_mobile = models.IntegerField(blank = True, null = True)


class Project(models.Model):
    project_name = models.CharField(max_length=100)
    repo_url = models.CharField(max_length=200)
    clone_url = models.CharField(max_length=200)
    private = models.BooleanField(default=False)
    core_user = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    commits_url = models.CharField(max_length=200)
    project_path = models.CharField(max_length=200, blank=True, null=True)
    language = models.CharField(max_length=20, blank=True, null=True)
    def __str__(self):
        return self.project_name
