# coding: utf-8

import unittest
from signal import SIGINT, SIGKILL
from time import sleep
from subprocess import Popen, PIPE
import shlex
import zmq


time_to_sleep = 0.15

class TestManager(unittest.TestCase):
    def setUp(self):
        self.context = zmq.Context()
        self.start_manager_process()

    def tearDown(self):
        self.end_manager_process()
        self.context.destroy()

    def start_manager_process(self):
        #TODO: call process passing a configuration file
        self.manager = Popen(shlex.split('python ./pypln/manager.py'),
                             stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for line in self.manager.stdout.readline():
            if 'main loop' in line:
                break

    def end_manager_process(self):
        self.manager.send_signal(SIGINT)
        sleep(time_to_sleep)
        self.manager.send_signal(SIGKILL)
        self.manager.wait()

    def test_connect_to_manager_api_zmq_socket_and_execute_undefined_command(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'spam': 'eggs'})
        sleep(time_to_sleep)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message, {'answer': 'undefined command'})

    def test_should_connect_to_manager_api_zmq_socket(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'command': 'hello'})
        sleep(time_to_sleep)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message, {'answer': 'unknown command'})

    def test_should_connect_to_manager_broadcast_zmq_socket(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        broadcast = self.context.socket(zmq.SUB)
        broadcast.connect('tcp://localhost:5556')
        broadcast.setsockopt(zmq.SUBSCRIBE, 'new job')
        api.send_json({'command': 'add job', 'worker': 'x', 'document': 'y'})
        sleep(time_to_sleep)
        api.recv_json()
        try:
            message = broadcast.recv(zmq.NOBLOCK)
        except zmq.ZMQError:
            self.assertFalse("Didn't receive 'new job' from broadcast")
        else:
            self.assertEquals(message, 'new job')

    def test_command_get_configuration_should_return_dict_passed_on_setUp(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'command': 'get configuration'})
        default_config = {'db': {'host': 'localhost', 'port': 27017,
                                 'database': 'pypln',
                                 'collection': 'documents',
                                 'gridfs-collection': 'files'}}
        sleep(time_to_sleep)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message, default_config)

    def test_command_add_job_should_return_a_job_id(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        cmd = {'command': 'add job', 'worker': 'test', 'document': 'eggs'}
        api.send_json(cmd)
        sleep(time_to_sleep)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message['answer'], 'job accepted')
            self.assertIn('job id', message)
            self.assertEquals(len(message['job id']), 32)

    def test_command_get_job_should_return_empty_if_no_job(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'command': 'get job'})
        sleep(time_to_sleep)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message['worker'], None)

    def test_command_get_job_should_return_a_job_after_adding_one(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'command': 'add job', 'worker': 'spam',
                       'document': 'eggs'})
        sleep(time_to_sleep)
        job = api.recv_json()
        api.send_json({'command': 'get job'})
        sleep(time_to_sleep)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message['worker'], 'spam')
            self.assertEquals(message['document'], 'eggs')
            self.assertIn('job id', message)
            self.assertEquals(len(message['job id']), 32)

    def test_finished_job_without_job_id_should_return_error(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'command': 'finished job'})
        sleep(time_to_sleep)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message['answer'], 'syntax error')

    def test_finished_job_with_unknown_job_id_should_return_error(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'command': 'finished job', 'job id': 'python rules'})
        sleep(time_to_sleep)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message['answer'], 'unknown job id')

    def test_finished_job_with_correct_job_id_should_return_good_job(self):
        api = self.context.socket(zmq.REQ)
        api.connect('tcp://localhost:5555')
        api.send_json({'command': 'add job', 'worker': 'a', 'document': 'b'})
        message = api.recv_json()
        api.send_json({'command': 'finished job', 'job id': message['job id']})
        sleep(time_to_sleep)
        try:
            message = api.recv_json(zmq.NOBLOCK)
        except zmq.ZMQError:
            self.assertFalse('Exception raised, socket not connected')
        else:
            self.assertEquals(message['answer'], 'good job!')
