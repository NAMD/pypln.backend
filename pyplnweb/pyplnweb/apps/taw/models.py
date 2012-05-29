from django.db import models
from profiles.models import Profile
from django.contrib.auth.models import User

class Document(models.Model):
    """
    All metadata about documents should be stored in Mongodb
    this is just a link
    """
    mongoid = models.CharField(max_length=24) # MongoDB object id
    database = models.CharField(max_length=64) # name of mongodb databas
    collection = models.CharField(max_length=64) #Name of the collection the document belongs to

    def __unicode__(self):
        return self.mongoid

class Corpus(models.Model):
    """
    These sets of documents can be created and destroyed by users without affecting the
    included documents-
    """
    title = models.CharField(max_length=128,unique=True)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User)
    docs = models.ManyToManyField(Document)

    class Meta:
        ordering = ["-title"]
        verbose_name_plural = 'corpora'

    def __unicode__(self):
        return self.title
#  Collection  model Deprecated, we will reserve the concept of collection to actual collections in mongodb
#class Collection(models.Model):
#    """
#    Collections are sets of multiple corpora. These are not the same as mongodb collections.
#    """
#    title = models.CharField(max_length=128)
#    date_created = models.DateTimeField(auto_now_add=True)
#    date_modified = models.DateTimeField(auto_now=True)
#    owner = models.ForeignKey(Profile)
#    corpora = models.ManyToManyField(Corpus)
#
#    class Meta:
#        ordering = ["-title","-date_created"]
#
#    def __unicode__(self):
#        return self.title

class Glossario(models.Model):
    """
    Collections of words created by users
    """
    title = models.CharField(max_length=128)
    description = models.TextField()
    owner = models.ForeignKey(Profile)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)