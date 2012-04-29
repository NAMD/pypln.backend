# -*- coding: utf-8 -*-
u"""
Testing module for cmanager.py

license: GPL v3 or later
"""
__docformat__ = "restructuredtext en"

import unittest
from pypln.apps.cluster.cmanager import Manager, get_ipv4_address
import subprocess
import zmq
import time
import os,signal
from pypln.testing import zmqtesting

class TestManagerComm(unittest.TestCase):
    def setUp(self):
        self.managerproc = subprocess.Popen(['./cmanager.py', '-c','pypln.test.conf'])
        self.context = zmq.Context()
        self.req_sock = zmqtesting.make_sock(context=self.context, sock_type=zmq.REQ,connect=(get_ipv4_address(), 5550))
        time.sleep(2)
    def tearDown(self):
        self.req_sock.close()
        self.context.term()
        os.kill(self.managerproc.pid,signal.SIGINT)
        self.managerproc.terminate()

    def test_manager_send_one_message(self):
        self.req_sock.send_json('{job:"job"}')
        msg = self.req_sock.recv_json()
        self.assertEqual(msg,"{ans:'Job queued'}")


    def testing_sending_many_messages(self):
        pass
#        local('./slavedriver.py 127.0.0.1:5551')
        msgs = [{'jobid':12, 'data':'fksdjfhlaksf'}]*10
        self.req_sock.send_json(msgs)
        msg = self.req_sock.recv_json()
        self.assertEqual(msg,"{ans:'Job queued'}")
        #send again
        self.req_sock.send_json(msgs)
        msg = self.req_sock.recv_json()
        self.assertEqual(msg,"{ans:'Job queued'}")


#        local('killall slavedriver.py')

class TestManagerInst(unittest.TestCase):
    def test_load_config_file(self):
        M = Manager('pypln.test.conf',False)
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

    def test_manager_bind(self):
        M = Manager('pypln.test.conf',True)
        M.streamer.terminate()
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()