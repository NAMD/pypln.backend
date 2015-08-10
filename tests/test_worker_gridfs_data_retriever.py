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
import bson
from gridfs import GridFS
from pypln.backend.workers import GridFSDataRetriever
from pypln.backend import config
from utils import TaskTest

class TestGridFSDataRetrieverWorker(TaskTest):
    def test_extract_file_data_from_GridFS(self):
        content = "File content"
        gridfs = GridFS(self.db,
                collection=config.MONGODB_CONFIG['gridfs_collection'])
        new_file_id = gridfs.put(content)
        expected_file_data = gridfs.get(new_file_id)

        data = {'file_id': str(new_file_id)}
        doc_id = self.collection.insert(data)
        GridFSDataRetriever().delay(doc_id)
        refreshed_document = self.collection.find_one({'_id': doc_id})

        self.assertEqual(refreshed_document['contents'],
                base64.b64encode(content))
        self.assertEqual(refreshed_document['length'],
                expected_file_data.length)
        self.assertEqual(refreshed_document['md5'], expected_file_data.md5)
        self.assertEqual(refreshed_document['filename'],
                expected_file_data.filename)
        self.assertEqual(refreshed_document['upload_date'],
                expected_file_data.upload_date)
        self.assertEqual(refreshed_document['contents'],
                base64.b64encode(expected_file_data.read()))

    def test_task_raises_exception_when_file_does_not_exist(self):
        data = {'file_id': "Inexistent document"}
        doc_id = self.collection.insert(data)
        result = GridFSDataRetriever().delay(doc_id)
        refreshed_document = self.collection.find_one({'_id': doc_id})

        self.assertTrue(result.failed())
        self.assertEqual(result.status, "FAILURE")
        self.assertIsInstance(result.info, bson.errors.InvalidId)
