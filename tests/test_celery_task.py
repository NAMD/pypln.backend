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
from pypln.backend.celery_task import PyPLNTask
from utils import TaskTest

class FakeTask(PyPLNTask):
    def process(self, document):
        return {'result': document['input']}

class TestCeleryTask(TaskTest):
    def test_task_should_get_the_correct_document(self):
        """This is a regression test. PyPLNTask was not filtering by _id. It
        was getting the first document it found. """

        # This is just preparing the expected input in the database
        wrong_doc_id = self.collection.insert({'input': 'wrong'}, w=1)
        correct_doc_id = self.collection.insert({'input': 'correct'}, w=1)

        FakeTask().delay(correct_doc_id)

        refreshed_doc = self.collection.find_one({'_id': correct_doc_id})

        self.assertEqual(refreshed_doc['result'], 'correct')
