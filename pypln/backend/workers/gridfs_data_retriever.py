# coding: utf-8
#
# Copyright 2015 NAMD-EMAP-FGV
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
import base64
from bson import ObjectId
from gridfs import GridFS
import pymongo
from pypln.backend.celery_task import PyPLNTask
from pypln.backend import config

class GridFSDataRetriever(PyPLNTask):

    def process(self, document):
        database = pymongo.MongoClient(host=config.MONGODB_CONFIG['host'],
                port=config.MONGODB_CONFIG['port']
            )[config.MONGODB_CONFIG['database']]
        gridfs = GridFS(database, config.MONGODB_CONFIG['gridfs_collection'])

        file_data = gridfs.get(ObjectId(document['file_id']))

        # We decided to store 'contents' as a base64 encoded string in the
        # database to avoid possible corruption of files. For example: when
        # it's a pdf, the process of storing the data as utf-8 in mongo might
        # be corrupting the file.  This wasn't a problem before, because
        # MongoDict pickled everything before storing.
        contents = base64.b64encode(file_data.read())

        result = {'length': file_data.length,
                  'md5': file_data.md5,
                  'filename': file_data.filename,
                  'upload_date': file_data.upload_date,
                  'contents': contents}
        return result
