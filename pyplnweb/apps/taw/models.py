from django.db import models
from profiles.models import Profile
from django.contrib.auth.models import User

class Corpus:
    pass

class Glossario(models.Model):
    """
    Collections of words created by users
    """
    title = models.CharField(max_length=128)
    description = models.TextField()
    owner = models.ForeignKey(Profile)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
