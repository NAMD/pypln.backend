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

from pypln.backend.celery_task import PyPLNTask
from elasticsearch import Elasticsearch
from pypln.backend.config import ELASTICSEARCH_CONFIG

ES = Elasticsearch(hosts=ELASTICSEARCH_CONFIG['hosts'])

class ElasticIndexer(PyPLNTask):
    """
    Index document in an elasticsearch index specified in the document as `index_name`.
    """
    def process(self, document):
        index_name = document.pop("index_name")
        doc_type = document.pop('doc_type')
        file_id = document["file_id"]
        ES.indices.create(index_name, ignore=400)
        result = ES.index(index=index_name, doc_type=doc_type,
                body=document, id=file_id)
        return result
