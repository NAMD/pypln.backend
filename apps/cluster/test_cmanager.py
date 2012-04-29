# -*- coding: utf-8 -*-
u"""
Testing module for cmanager.py

license: GPL v3 or later
"""
__docformat__ = "restructuredtext en"

import unittest
from cmanager import Manager, get_ipv4_address
from fabric.api import local
import subprocess
import zmq
import time

class TestManager(unittest.TestCase):
    def setUp(self):
        self.context = zmq.Context()
        self.sock = self.context.socket(zmq.REQ)
    def tearDown(self):
        self.sock.close()
        self.context.term()

    def test_load_config_file(self):
        M = Manager('pypln.test.conf')
        self.assertTrue(M.config.has_section('cluster'))
        self.assertTrue(M.config.has_section('zeromq'))
        self.assertTrue(M.config.has_section('authentication'))
        self.assertTrue(M.config.has_section('streamer'))
        self.assertTrue(M.config.has_section('slavedriver'))
        self.assertTrue(M.config.has_section('worker'))
        self.assertTrue(M.config.has_section('sink'))


    def test_manager_bind(self):
        M = Manager('pypln.test.conf',True)
        M.streamer.terminate()
        self.assertTrue(True)


    def test_manager_run(self):
        ip = get_ipv4_address()
        P = subprocess.Popen(['./cmanager.py', '-c','pypln.test.conf'])
        time.sleep(2)
        self.sock.connect('tcp://%s:5550'%ip)
        self.sock.send_json('{job:"job"}')
        time.sleep(2)
#        print self.sock.recv_json()
        P.terminate()

    def test_bootstrap_cluster(self):
        M = Manager('pypln.test.conf',True)
        self.assertTrue(M.streamer.is_alive())
        M.streamer.terminate()


    def testing_sending_messages(self):
#        local('./slavedriver.py 127.0.0.1:5551')
        M = Manager('pypln.test.conf',True)
#        M.run()
        msgs = [{'jobid':12, 'data':'fksdjfhlaksf'}]*100
#        M.push_load(msgs)
        M.streamer.terminate()

#        local('killall slavedriver.py')



if __name__ == '__main__':
    unittest.main()