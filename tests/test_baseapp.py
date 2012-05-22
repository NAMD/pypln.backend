# -*- coding: utf-8 -*-
u"""
Testing module for cmanager.py

license: GPL v3 or later
"""
__docformat__ = "restructuredtext en"

import unittest
from pypln.servers.baseapp import TaskVentilator
from pypln.servers.ventilator import Ventilator
from pypln.workers.dummy_worker import DummyWorker
from pypln.sinks.dummy_sink import DummySink


class TestTaskVentilator(unittest.TestCase):
    def test_instantiate(self):
        tv = TaskVentilator(Ventilator, DummyWorker, DummySink, 10)
        self.assertEqual(tv.ports['ventilator'][0], tv.ports['worker'][1])
        self.assertEqual(tv.ports['ventilator'][1], tv.ports['sink'][2])
        self.assertEqual(tv.ports['worker'][0], tv.ports['sink'][0])
        self.assertEqual(tv.ports['worker'][2], tv.ports['sink'][1])
        self.assertEqual(tv.ports['ventilator'][2], tv.ports['worker'][2])
