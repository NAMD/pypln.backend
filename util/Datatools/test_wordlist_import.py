__author__ = 'fccoelho'

import unittest
from wordlist_import import *
from glob import glob
import os

class WordlistImport(unittest.TestCase):
    def test_show_available_dicts(self):
        dict_list = []
        for l in glob("/usr/share/dict/*"):
            if os.path.islink(l):
                continue
            f = os.path.split(l)[-1]
            if f.startswith('README'):
                continue
            dict_list.append(l)
        self.assertEqual(dict_list, get_dict_list())

if __name__ == '__main__':
    unittest.main()
