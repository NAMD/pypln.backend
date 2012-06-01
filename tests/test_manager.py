# coding: utf-8

import unittest
import os
import signal
import time
from multiprocessing import Process
import zmq
from pypln.manager import Manager


def run_manager(config, api_host_port, broadcast_host_port):
    manager = Manager(config)
    manager.bind(api_host_port, broadcast_host_port)
    manager.run()

class TestManager(unittest.TestCase):
    def setUp(self):
        args = ({'db': {'host': 'localhost', 'port': 27917,
                        'collection': 'pypln'}}, ('*', 5555), ('*', 5556))
        self.manager = Process(target=run_manager, args=args)
        self.manager.start()
        time.sleep(0.1)
        self.context = zmq.Context()

    def tearDown(self):
        self.context.term()
        os.kill(self.manager.pid, signal.SIGINT)
        self.manager.join()

    def test_should_connect_to_manager_api_zmq_socket(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'command': 'hello'})
        time.sleep(0.01)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message, {'answer': 'unknown command'})
        finally:
            api.close()

    def test_should_connect_to_manager_broadcast_zmq_socket(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        broadcast = self.context.socket(zmq.SUB)
        broadcast.connect('tcp://localhost:5556')
        broadcast.setsockopt(zmq.SUBSCRIBE, 'new job')
        api.send_json({'command': 'add job', 'worker': 'x', 'document': 'y'})
        api.recv_json()
        try:
            message = broadcast.recv(zmq.NOBLOCK)
        except zmq.ZMQError:
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message, 'new job')
        finally:
            api.close()
            broadcast.close()
