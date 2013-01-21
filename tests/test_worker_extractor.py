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
from textwrap import dedent
from pypln.backend.workers import Extractor


class TestExtractorWorker(unittest.TestCase):
    def test_extraction_from_text_file(self):
        expected = "This is a test file.\nI'm testing PyPLN extractor worker!"
        filename = 'tests/data/test.txt'
        data = {'filename': filename, 'contents': open(filename).read()}
        result = Extractor().process(data)
        metadata = result['file_metadata']
        self.assertEqual(expected, result['text'])
        self.assertEqual(metadata, {})

    def test_extraction_from_html_file(self):
        expected = "This is a test file. I'm testing PyPLN extractor worker!"
        filename = 'tests/data/test.html'
        data = {'filename': filename, 'contents': open(filename).read()}
        result = Extractor().process(data)
        metadata = result['file_metadata']
        self.assertEqual(expected, result['text'])
        self.assertEqual(metadata, {})

    def test_extraction_from_pdf_file(self):
        expected = "This is a test file.\nI'm testing PyPLN extractor worker!"
        filename = 'tests/data/test.pdf'
        data = {'filename': filename, 'contents': open(filename).read()}
        result = Extractor().process(data)
        metadata = result['file_metadata']
        metadata_expected = {
                'Author':         'Álvaro Justen',
                'Creator':        'Writer',
                'Producer':       'LibreOffice 3.5',
                'CreationDate':   'Fri Jun  1 17:07:57 2012',
                'Tagged':         'no',
                'Pages':          '1',
                'Encrypted':      'no',
                'Page size':      '612 x 792 pts (letter)',
                'Optimized':      'no',
                'PDF version':    '1.4',
        }
        self.assertEqual(expected, result['text'])
        self.assertEqual(metadata, metadata_expected)

    def test_extraction_from_html(self):
        contents = dedent('''
        <html>
          <head>
            <title>Testing</title>
            <script type="text/javascript">this must not appear</script>
            <style type="text/css">this must not appear [2]</style>
          </head>
          <body>
            python test1
            <br>
            test2
            <table>
              <tr><td>spam</td></tr>
              <tr><td>eggs</td></tr>
              <tr><td>ham</td></tr>
            </table>
            test3
            <div>test4</div>test5
            <span>test6</span>test7
            <h1>bla1</h1> bla2
          </body>
        </html>
        ''')
        data = {'filename': 'test.html', 'contents': contents}
        result = Extractor().process(data)
        expected = dedent('''
            Testing

            python test1
            test2

            spam
            eggs
            ham

            test3
            test4
            test5 test6 test7

            bla1

            bla2''').strip()
        self.assertEqual(result['text'], expected)

    def test_language_detection(self):
        text_pt = 'Esse texto foi escrito por Álvaro em Português.'
        text_es = 'Este texto ha sido escrito en Español por Álvaro.'
        text_en = 'This text was written by Álvaro in English.'
        data_pt = {'filename': 'text-pt.txt', 'contents': text_pt}
        data_es = {'filename': 'text-es.txt', 'contents': text_es}
        data_en = {'filename': 'text-en.txt', 'contents': text_en}
        result_pt = Extractor().process(data_pt)
        result_es = Extractor().process(data_es)
        result_en = Extractor().process(data_en)
        self.assertEqual('pt', result_pt['language'])
        self.assertEqual('es', result_es['language'])
        self.assertEqual('en', result_en['language'])

    def test_unescape_html_entities(self):
        expected = (u"This text has html <entities>. Álvaro asked me to make"
                     " sure it also has non ascii chars.")
        filename = 'tests/data/test_html_entities.txt'
        data = {'filename': filename, 'contents': open(filename).read()}
        result = Extractor().process(data)
        self.assertEqual(expected, result['text'])

    def test_should_detect_encoding_and_return_a_unicode_object(self):
        expected = u"Flávio"
        filename = 'tests/data/test_iso-8859-1.txt'
        data = {'filename': filename, 'contents': open(filename).read()}
        result = Extractor().process(data)
        self.assertEqual(expected, result['text'])
        self.assertEqual(type(result['text']), unicode)

    def test_unkown_mimetype_should_be_flagged(self):
        filename = 'tests/data/random_file'
        # we can't put the expected text content here, so we'll just make sure
        # it's equal to the input content, since
        contents = open(filename).read()
        data = {'filename': filename, 'contents': contents}
        result = Extractor().process(data)
        self.assertFalse(result.has_key('file_metadata'))
        self.assertFalse(result.has_key('language'))
        self.assertEqual(result['unsupported_mimetype'], True)
        self.assertEqual(result['text'], "")
