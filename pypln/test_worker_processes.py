#-*- coding:utf-8 -*-
"""
This testing module contains tests of the process methods of workers
These methods should be called directly, with a message, to avoid the need of starting
ventilators and worker processes communicating through ZMQ

Created on 27/02/12
by Flávio Codeço Coelho
"""
__author__ = 'fccoelho'

import unittest
from workers.highlighter_worker import HighlighterWorker

class TestHighlighterWorker(unittest.TestCase):
    def setUp(self):
        self.W = HighlighterWorker()
    def tearDown(self):
        pass

    def test_single_wordlist(self):
        msg = {'text':['atirei','o','pau','no','gato'],'wordlists':{'um':['pau','gato']}}
        res = self.W.process(msg)
        self.assertDictEqual(res,{'highlighted_text':['atirei','o','<span class="tagged" title="um"><b>pau</b></span>',
                                                  'no','<span class="tagged" title="um"><b>gato</b></span>']})

    def test_multiple_wordlist(self):
        msg = {'text':['atirei','o','pau','no','gato'],
               'wordlists':{'um':['pau','gato'],'dois':['pau','cachorro']}}
        res = self.W.process(msg)
        self.assertDictEqual(res,{'highlighted_text':['atirei','o','<span class="tagged" title="um,dois"><b>pau</b></span>',
                                                  'no','<span class="tagged" title="um"><b>gato</b></span>']})

if __name__ == '__main__':
    unittest.main()