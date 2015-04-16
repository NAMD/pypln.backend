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
from mongodict import MongoDict
from nltk import word_tokenize, sent_tokenize

from pypln.backend.celery_app import app



@app.task(name='workers.Tokenizer')
def Tokenizer(document_id):
    db = MongoDict(database="pypln_backend_test")
    text = db['id:{}:text'.format(document_id)]

    tokens = word_tokenize(text)
    sentences = [word_tokenize(sent) for sent in sent_tokenize(text)]

    db['id:{}:tokens'.format(document_id)] = tokens
    db['id:{}:sentences'.format(document_id)] = sentences

    return document_id
