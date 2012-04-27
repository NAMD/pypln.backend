# -*- coding: utf-8 -*-
u"""
Testing module for cmanager.py

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
        M = Manager('pypln.test.conf')
        self.assertTrue(M.config.has_section('cluster'))
        self.assertTrue(M.config.has_section('zeromq'))
        self.assertTrue(M.config.has_section('authentication'))
        self.assertTrue(M.config.has_section('streamer'))
        self.assertTrue(M.config.has_section('slavedriver'))
        self.assertTrue(M.config.has_section('worker'))
        self.assertTrue(M.config.has_section('sink'))
    def test_bootstrap_cluster(self):
        M = Manager('pypln.test.conf',True)
        self.assertTrue(M.streamer.is_alive())
        M.streamer.terminate()



if __name__ == '__main__':
    unittest.main()