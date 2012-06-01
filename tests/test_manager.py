# coding: utf-8

import unittest
import os
import signal
from time import sleep
from multiprocessing import Process
import zmq
from pypln.manager import Manager


sleep_time = 0.15
sleep_time_process = 0.1

def run_manager(config, api_host_port, broadcast_host_port):
    manager = Manager(config)
    manager.bind(api_host_port, broadcast_host_port)
    manager.run()

class TestManager(unittest.TestCase):
    def setUp(self):
        self.config = {'db': {'host': 'localhost', 'port': 27917,
                       'collection': 'pypln'}}
        args = (self.config, ('*', 5555), ('*', 5556))
        self.manager = Process(target=run_manager, args=args)
        self.manager.start()
        sleep(sleep_time_process)
        self.context = zmq.Context()

    def tearDown(self):
        self.context.destroy()
        os.kill(self.manager.pid, signal.SIGINT)
        self.manager.join()

    def test_should_connect_to_manager_api_zmq_socket_and_execute_undefined_command(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'spam': 'eggs'})
        sleep(sleep_time)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            api.close()
            self.assertFalse('Exception raised, socket not connected')
        else:
            api.close()
            self.assertEquals(message, {'answer': 'undefined command'})

    def test_should_connect_to_manager_api_zmq_socket(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'command': 'hello'})
        sleep(sleep_time)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            api.close()
            self.assertFalse('Exception raised, socket not connected')
        else:
            api.close()
            self.assertEquals(message, {'answer': 'unknown command'})

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
            api.close()
            broadcast.close()
            self.assertFalse('Exception raised, socket not connected')
        else:
            api.close()
            broadcast.close()
            self.assertEquals(message, 'new job')

    def test_command_get_configuration_should_return_dict_passed_on_setUp(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'command': 'get configuration'})
        sleep(sleep_time)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            api.close()
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message, self.config)
            api.close()

    def test_command_add_job_should_return_a_job_id(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        cmd = {'command': 'add job', 'worker': 'test', 'document': 'eggs'}
        api.send_json(cmd)
        sleep(sleep_time)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            api.close()
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message['answer'], 'job accepted')
            self.assertIn('job id', message)
            self.assertEquals(len(message['job id']), 32)
            api.close()

    def test_command_get_job_should_return_empty_if_no_job(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'command': 'get job'})
        sleep(sleep_time)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            api.close()
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message['worker'], None)
            api.close()

    def test_command_get_job_should_return_a_job_after_adding_one(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'command': 'add job', 'worker': 'spam',
                       'document': 'eggs'})
        job = api.recv_json()
        api.send_json({'command': 'get job'})
        sleep(sleep_time)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            api.close()
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message['worker'], 'spam')
            self.assertEquals(message['document'], 'eggs')
            self.assertIn('job id', message)
            self.assertEquals(len(message['job id']), 32)
            api.close()

    def test_finished_job_without_job_id_should_return_error(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'command': 'finished job'})
        sleep(sleep_time)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            api.close()
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message['answer'], 'syntax error')
            api.close()

    def test_finished_job_with_unknown_job_id_should_return_error(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'command': 'finished job', 'job id': 'python rules'})
        sleep(sleep_time)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            api.close()
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message['answer'], 'unknown job id')
            api.close()

    def test_finished_job_with_correct_job_id_should_return_good_job(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'command': 'add job', 'worker': 'a', 'document': 'b'})
        message = api.recv_json()
        api.send_json({'command': 'finished job', 'job id': message['job id']})
        sleep(sleep_time)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            api.close()
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message['answer'], 'good job!')
            api.close()
