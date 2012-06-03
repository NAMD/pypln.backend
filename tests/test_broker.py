# coding: utf-8

import unittest
from signal import SIGINT, SIGKILL
from time import sleep
from subprocess import Popen, PIPE
import shlex
import zmq


time_to_sleep = 0.2

def run_broker(api_host_port, broadcast_host_port):
    broker = ManagerBroker()
    broker.connect(api_host_port, broadcast_host_port)
    broker.run()

class TestManagerBroker(unittest.TestCase):
    def setUp(self):
        self.start_broker_process()
        self.context = zmq.Context()

    def start_broker_process(self):
        self.broker = Popen(shlex.split('python ./pypln/broker.py'),
                            stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for line in self.broker.stdout.readline():
            if 'main loop' in line:
                break

    def end_broker_process(self):
        self.broker.send_signal(SIGINT)
        sleep(time_to_sleep)
        self.broker.send_signal(SIGKILL)
        self.broker.wait()

    def start_manager_sockets(self):
        self.api = self.context.socket(zmq.REP)
        self.broadcast = self.context.socket(zmq.PUB)
        self.api.bind('tcp://*:5555')
        self.broadcast.bind('tcp://*:5556')
        sleep(time_to_sleep)

    def close_sockets(self):
        self.api.close()
        self.broadcast.close()

    def tearDown(self):
        self.context.destroy()
        self.end_broker_process()

    def test_should_ask_for_configuration_on_start(self):
        self.start_manager_sockets()
        try:
            message = self.api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            self.close_sockets()
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.api.send_json({'db': {'host': 'localhost', 'port': 27017,
                                       'database': 'pypln',
                                       'collection': 'documents',
                                       'gridfs-collection': 'files'}})
            #TODO: pass the configuration through configuration file when
            #      starting the process
            self.assertEquals(message, {'command': 'get configuration'})
            self.close_sockets()
