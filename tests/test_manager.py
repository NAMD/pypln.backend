# coding: utf-8

import unittest
from signal import SIGINT, SIGKILL
from time import sleep
from subprocess import Popen, PIPE
import shlex
import zmq


time_to_wait = 150

class TestManager(unittest.TestCase):
    def setUp(self):
        self.context = zmq.Context()
        self.start_manager_process()
        self.api = self.context.socket(zmq.REQ)
        self.api.connect('tcp://localhost:5555')
        self.broadcast = self.context.socket(zmq.SUB)
        self.broadcast.connect('tcp://localhost:5556')
        self.broadcast.setsockopt(zmq.SUBSCRIBE, 'new job')

    def tearDown(self):
        self.end_manager_process()
        self.close_sockets()
        self.context.term()

    def start_manager_process(self):
        #TODO: call process passing a configuration file
        self.manager = Popen(shlex.split('python ./pypln/manager.py'),
                             stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for line in self.manager.stdout.readline():
            if 'main loop' in line:
                break

    def end_manager_process(self):
        self.manager.send_signal(SIGINT)
        sleep(time_to_wait / 1000.0)
        self.manager.send_signal(SIGKILL)
        self.manager.wait()

    def close_sockets(self):
        self.api.close()
        self.broadcast.close()

    def test_connect_to_manager_api_zmq_socket_and_execute_undefined_command(self):
        self.api.send_json({'spam': 'eggs'})
        if not self.api.poll(time_to_wait):
            self.assertFalse('Exception raised, socket not connected')
        message = self.api.recv_json()
        self.assertEquals(message, {'answer': 'undefined command'})

    def test_should_connect_to_manager_api_zmq_socket(self):
        self.api.send_json({'command': 'hello'})
        if not self.api.poll(time_to_wait):
            self.assertFalse('Exception raised, socket not connected')
        message = self.api.recv_json()
        self.assertEquals(message, {'answer': 'unknown command'})

    def test_should_connect_to_manager_broadcast_zmq_socket(self):
        self.api.send_json({'command': 'add job', 'worker': 'x',
                            'document': 'y'})
        if not self.api.poll(time_to_wait):
            self.assertFalse("Didn't receive 'add job' reply")
        self.api.recv_json()
        if not self.broadcast.poll(time_to_wait):
            self.assertFalse("Didn't receive 'new job' from broadcast")
        message = self.broadcast.recv()
        self.assertEquals(message, 'new job')

    def test_command_get_configuration_should_return_dict_passed_on_setUp(self):
        self.api.send_json({'command': 'get configuration'})
        default_config = {'db': {'host': 'localhost', 'port': 27017,
                                 'database': 'pypln',
                                 'collection': 'documents',
                                 'gridfs-collection': 'files'}}
        if not self.api.poll(time_to_wait):
            self.assertFalse('Exception raised, socket not connected')
        message = self.api.recv_json()
        self.assertEquals(message, default_config)

    def test_command_add_job_should_return_a_job_id(self):
        cmd = {'command': 'add job', 'worker': 'test', 'document': 'eggs'}
        self.api.send_json(cmd)
        if not self.api.poll(time_to_wait):
            self.assertFalse('Exception raised, socket not connected')
        message = self.api.recv_json()
        self.assertEquals(message['answer'], 'job accepted')
        self.assertIn('job id', message)
        self.assertEquals(len(message['job id']), 32)

    def test_command_get_job_should_return_empty_if_no_job(self):
        self.api.send_json({'command': 'get job'})
        if not self.api.poll(time_to_wait):
            self.assertFalse('Exception raised, socket not connected')
        message = self.api.recv_json()
        self.assertEquals(message['worker'], None)

    def test_command_get_job_should_return_a_job_after_adding_one(self):
        self.api.send_json({'command': 'add job', 'worker': 'spam',
                            'document': 'eggs'})
        if not self.api.poll(time_to_wait):
            self.assertFalse("Didn't receive 'add job' reply")
        job = self.api.recv_json()
        self.api.send_json({'command': 'get job'})
        if not self.api.poll(time_to_wait):
            self.assertFalse('Exception raised, socket not connected')
        message = self.api.recv_json()
        self.assertEquals(message['worker'], 'spam')
        self.assertEquals(message['document'], 'eggs')
        self.assertIn('job id', message)
        self.assertEquals(len(message['job id']), 32)

    def test_finished_job_without_job_id_should_return_error(self):
        self.api.send_json({'command': 'finished job'})
        if not self.api.poll(time_to_wait):
            self.assertFalse('Exception raised, socket not connected')
        message = self.api.recv_json()
        self.assertEquals(message['answer'], 'syntax error')

    def test_finished_job_with_unknown_job_id_should_return_error(self):
        self.api.send_json({'command': 'finished job', 'job id': 'python rlz'})
        if not self.api.poll(time_to_wait):
            self.assertFalse('Exception raised, socket not connected')
        message = self.api.recv_json()
        self.assertEquals(message['answer'], 'unknown job id')

    def test_finished_job_with_correct_job_id_should_return_good_job(self):
        self.api.send_json({'command': 'add job', 'worker': 'a',
                            'document': 'b'})
        if not self.api.poll(time_to_wait):
            self.assertFalse("Didn't receive 'add job' reply")
        message = self.api.recv_json()
        self.api.send_json({'command': 'finished job',
                            'job id': message['job id']})
        if not self.api.poll(time_to_wait):
            self.assertFalse('Exception raised, socket not connected')
        message = self.api.recv_json()
        self.assertEquals(message['answer'], 'good job!')
