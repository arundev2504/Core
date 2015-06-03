from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CoreUser(AbstractUser):
    user_token = models.CharField(max_length=200, blank = True, null = True)
    user_mobile = models.IntegerField(blank = True, null = True)


class Project(models.Model):
    project_name = models.CharField(max_length=100)
    repo_url = models.CharField(max_length=200)
    clone_url = models.CharField(max_length=200)

