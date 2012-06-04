# coding: utf-8

import unittest
from signal import SIGINT, SIGKILL
from time import sleep
from subprocess import Popen, PIPE
import shlex
import zmq


time_to_wait = 150

class TestManagerBroker(unittest.TestCase):
    def setUp(self):
        self.context = zmq.Context()
        self.start_manager_sockets()
        self.start_broker_process()

    def tearDown(self):
        self.end_broker_process()
        self.close_sockets()
        self.context.term()

    def start_broker_process(self):
        #TODO: call process passing a configuration file
        self.broker = Popen(shlex.split('python ./pypln/broker.py'),
                            stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for line in self.broker.stdout.readline():
            if 'main loop' in line:
                break

    def end_broker_process(self):
        self.broker.send_signal(SIGINT)
        sleep(time_to_wait / 1000.0)
        self.broker.send_signal(SIGKILL)
        self.broker.wait()

    def start_manager_sockets(self):
        self.api = self.context.socket(zmq.REP)
        self.broadcast = self.context.socket(zmq.PUB)
        self.api.bind('tcp://*:5555')
        self.broadcast.bind('tcp://*:5556')

    def close_sockets(self):
        self.api.close()
        self.broadcast.close()

    def test_should_ask_for_configuration_on_start(self):
        if self.api.poll(time_to_wait):
            message = self.api.recv_json()
            self.api.send_json({'db': {'host': 'localhost', 'port': 27017,
                                       'database': 'pypln',
                                       'collection': 'documents',
                                       'gridfs-collection': 'files'}})
            self.assertEquals(message, {'command': 'get configuration'})
        else:
            self.assertFalse('Exception raised, socket not connected')
