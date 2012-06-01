# coding: utf-8

import unittest
from pypln.workers import extractor


def clear_text(text):
    text = text.replace('\n', '')
    text = text.strip()
    while '  ' in text:
        text = text.replace('  ', ' ')
    text = text.replace(' . ', '.')
    return text

original_text = "This is a test file.I'm testing PyPLN extractor worker!"

class TestExtractor(unittest.TestCase):
    def test_extraction_from_text_file(self):
        filename = 'tests/test.txt'
        data = {'name': filename, 'contents': open(filename).read()}
        result = extractor.main(data)
        text = clear_text(result['text'])
        metadata = result['metadata']
        self.assertEquals(original_text, text)
        self.assertEquals(metadata, None)

    def test_extraction_from_html_file(self):
        filename = 'tests/test.html'
        data = {'name': filename, 'contents': open(filename).read()}
        result = extractor.main(data)
        text = clear_text(result['text'])
        metadata = result['metadata']
        self.assertEquals(original_text, text)
        self.assertEquals(metadata, None)

    def test_extraction_from_pdf_file(self):
        filename = 'tests/test.pdf'
        data = {'name': filename, 'contents': open(filename).read()}
        result = extractor.main(data)
        text = clear_text(result['text'])
        metadata = result['metadata']
        self.assertEquals(original_text, text)
        self.assertEquals(type(metadata), dict)
