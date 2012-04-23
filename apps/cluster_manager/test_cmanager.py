# -*- coding: utf-8 -*-
u"""
Testting module or cmanager.py

license: GPL v3 or later
"""
__date__ = 4 / 23 / 12
__docformat__ = "restructuredtext en"

import unittest

from cmanager import Manager

class TestManager(unittest.TestCase):
    def setUp(self):
        pass
    def test_load_config_file(self):
        M = Manager('pypln.conf')
        self.assertTrue(M.config.has_section('cluster'))
        self.assertTrue(M.config.has_section('zeromq'))
        self.assertTrue(M.config.has_section('authentication'))



if __name__ == '__main__':
    unittest.main()