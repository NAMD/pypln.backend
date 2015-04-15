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


class MongoDictById(MongoDict):
    #TODO: implement clear, __iter__, __len__ and contains with filters by id
    def __init__(self, doc_id, *args, **kwargs):
        self.doc_id = doc_id
        self.prefix = 'id:{}:'.format(self.doc_id)
        return super(MongoDictById, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        key = 'id:{}:{}'.format(self.doc_id, key)
        return super(MongoDictById, self).__setitem__(key, value)

    def __getitem__(self, key):
        key = 'id:{}:{}'.format(self.doc_id, key)
        return super(MongoDictById, self).__getitem__(key)

    def __delitem__(self, key):
        key = 'id:{}:{}'.format(self.doc_id, key)
        return super(MongoDictById, self).__delitem__(key)

    def __iter__(self):
        query_result = self._collection.find({'_id': {'$regex':
            '^{}'.format(self.prefix)}}, {'_id': 1})
        keys = (k['_id'].replace(self.prefix, '', 1) for k in query_result)
        return keys
