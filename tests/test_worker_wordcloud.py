# coding: utf-8
#
# Copyright 2014 NAMD-EMAP-FGV
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
from StringIO import StringIO

from PIL import Image

from pypln.backend.workers import WordCloud
from utils import TaskTest


class TestFreqDistWorker(TaskTest):
    name = "WordCloud"
    def test_wordcloud_should_return_a_base64_encoded_png(self):
        doc = {'freqdist':  [('is', 2), ('the', 2), ('blue', 1), ('sun', 1),
            ('sky', 1), (',', 1), ('yellow', 1), ('.', 1)], 'language': 'en'}
        doc_id = self.collection.insert(doc, w=1)
        WordCloud().delay(doc_id)

        refreshed_document = self.collection.find_one({'_id': doc_id})
        raw_png_data = base64.b64decode(refreshed_document['wordcloud'])

        fake_file = StringIO(raw_png_data)
        img = Image.open(fake_file)
        img.verify()
        self.assertEqual(img.format, 'PNG')
