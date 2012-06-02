# coding: utf-8

import unittest
import os
import signal
from time import sleep
from multiprocessing import Process
import zmq
from pypln.broker import ManagerBroker


sleep_time = 0.15
sleep_time_process = 0.1

def run_broker(api_host_port, broadcast_host_port):
    broker = ManagerBroker()
    sleep(0.5)
    broker.connect(api_host_port, broadcast_host_port)
    broker.run()

class TestManagerBroker(unittest.TestCase):
    def setUp(self):
        args = (('localhost', 5555), ('localhost', 5556))
        self.broker = Process(target=run_broker, args=args)
        self.broker.start()
        sleep(sleep_time_process)
        self.context = zmq.Context()

    def tearDown(self):
        self.context.destroy()
        os.kill(self.broker.pid, signal.SIGINT)
        self.broker.join()
