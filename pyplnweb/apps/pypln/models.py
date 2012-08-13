# coding: utf-8

import os
from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from settings import MONGODB_CONFIG
from pypln.storage import GridFSStorage


gridfs_storage = GridFSStorage(location='/',
                               host=MONGODB_CONFIG['host'],
                               port=MONGODB_CONFIG['port'],
                               database=MONGODB_CONFIG['database'],
                               collection=MONGODB_CONFIG['gridfs_collection'])

class Document(models.Model):
    blob = models.FileField(upload_to='/documents', storage=gridfs_storage)
    slug = models.SlugField()
    date_uploaded = models.DateTimeField()
    owner = models.ForeignKey(User)

    class Meta:
        ordering = ('blob', )

    def __unicode__(self):
        return self.blob.name

    def file_name(self):
        return os.path.basename(self.blob.name)

    def file_size(self):
        size = self.blob.size
        if size < 1024:
            return '{} B'.format(size)
        elif size < (1024 ** 2):
            return '{:.2f} KiB'.format(size / 1024.0)
        elif size < (1024 ** 3):
            return '{:.2f} MiB'.format(size / (1024.0 ** 2))
        else:
            return '{:.2f} GiB'.format(size / (1024.0 ** 3))

class Corpus(models.Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField(max_length=60)
    description = models.CharField(max_length=140)
    date_created = models.DateTimeField()
    last_modified = models.DateTimeField()
    owner = models.ForeignKey(User)
    documents = models.ManyToManyField(Document)

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return self.name

class CorpusForm(ModelForm):
    class Meta:
        model = Corpus
        fields = ('name', 'description')

class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ('blob', )
