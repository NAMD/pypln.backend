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

import bson
from gridfs import GridFS
from pypln.backend.workers import GridFSDataRetriever
from pypln.backend import config
from utils import TaskTest

class TestGridFSDataRetrieverWorker(TaskTest):
    def test_extract_file_data_from_GridFS(self):
        content = "File content"
        gridfs = GridFS(self.db, collection=config.GRIDFS_COLLECTION)
        new_file_id = gridfs.put(content)
        expected_file_data = gridfs.get(new_file_id)

        self.document['file_id'] = str(new_file_id)
        GridFSDataRetriever().delay(self.fake_id)

        self.assertEqual(self.document['contents'], content)
        self.assertEqual(self.document['length'], expected_file_data.length)
        self.assertEqual(self.document['md5'], expected_file_data.md5)
        self.assertEqual(self.document['filename'], expected_file_data.filename)
        self.assertEqual(self.document['upload_date'], expected_file_data.upload_date)
        self.assertEqual(self.document['contents'], expected_file_data.read())

    def test_task_raises_exception_when_file_does_not_exist(self):
        self.document['file_id'] = "Inexistent document"
        result = GridFSDataRetriever().delay(self.fake_id)
        self.assertTrue(result.failed())
        self.assertEqual(result.status, "FAILURE")
        self.assertIsInstance(result.info, bson.errors.InvalidId)
