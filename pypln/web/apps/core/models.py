# coding: utf-8
#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN. You can get more information at: http://pypln.org/.
#
# PyPLN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPLN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPLN.  If not, see <http://www.gnu.org/licenses/>.

import os
from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.conf import settings
from .storage import GridFSStorage


gridfs_storage = GridFSStorage(location='/',
                               host=settings.MONGODB_CONFIG['host'],
                               port=settings.MONGODB_CONFIG['port'],
                               database=settings.MONGODB_CONFIG['database'],
                               collection=settings.MONGODB_CONFIG['gridfs_collection'])

class Document(models.Model):
    blob = models.FileField(upload_to='/', storage=gridfs_storage)
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
