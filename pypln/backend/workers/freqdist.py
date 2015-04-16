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

from pypln.backend.celery_app import app
from pypln.backend.mongodict_adapter import MongoDictAdapter


@app.task
def freqdist(document_id):
    document = MongoDictAdapter(doc_id=document_id, database="pypln_backend_test")
    document_tokens = document['tokens']

    tokens = [info.lower() for info in document_tokens]
    frequency_distribution = {token: tokens.count(token) \
                              for token in set(tokens)}
    fd = frequency_distribution.items()
    fd.sort(lambda x, y: cmp(y[1], x[1]))

    document['freqdist'] = fd
    return document_id
