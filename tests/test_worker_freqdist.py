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

import unittest
from mongodict import MongoDict
from pypln.backend.workers import freqdist



class TestFreqDistWorker(unittest.TestCase):
    def test_freqdist_should_return_a_list_of_tuples_with_frequency_distribution(self):
        fake_id = '1234'
        tokens = ['The', 'sky', 'is', 'blue', ',', 'the', 'sun', 'is',
                  'yellow', '.']

        expected_fd =  [('is', 2), ('the', 2), ('blue', 1), ('sun', 1),
                ('sky', 1), (',', 1), ('yellow', 1), ('.', 1)]


        db = MongoDict(database="pypln_backend_test")
        # This is just preparing the expected input in the database
        db['id:{}:tokens'.format(fake_id)] = tokens
        #db['id:{}:language'.format(fake_id)] = 'en'

        # For some reason using `apply` instead of `delay` only works
        # after you've used the latter. For now we will use `delay`
        # and `get`.
        freqdist.delay(fake_id).get()

        # getting the results
        db = MongoDict(database="pypln_backend_test")

        resulting_fd = db['id:{}:freqdist'.format(fake_id)]

        self.assertEqual(resulting_fd, expected_fd)
