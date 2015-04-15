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
from pypelinin import Worker
from pypln.backend.celery_app import app



@app.task
def freqdist(document_id):
    db = MongoDict(database="pypln_backend_test")
    document_tokens = db['id:{}:tokens'.format(document_id)]

    tokens = [info.lower() for info in document_tokens]
    frequency_distribution = {token: tokens.count(token) \
                              for token in set(tokens)}
    fd = frequency_distribution.items()
    fd.sort(lambda x, y: cmp(y[1], x[1]))

    db['id:{}:freqdist'.format(document_id)] = fd
    return document_id
