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
            self.fail("Didn't receive 'undefined command' from manager")
        message = self.api.recv_json()
        self.assertEquals(message, {'answer': 'undefined command'})

    def test_should_connect_to_manager_api_zmq_socket(self):
        self.api.send_json({'command': 'hello'})
        if not self.api.poll(time_to_wait):
            self.fail("Didn't receive 'unknown command' from manager")
        message = self.api.recv_json()
        self.assertEquals(message, {'answer': 'unknown command'})

    def test_should_receive_new_job_from_broadcast_when_a_job_is_submitted(self):
        self.api.send_json({'command': 'add job', 'worker': 'x',
                            'document': 'y'})
        if not self.api.poll(time_to_wait):
            self.fail("Didn't receive 'add job' reply")
        self.api.recv_json()
        if not self.broadcast.poll(time_to_wait):
            self.fail("Didn't receive 'new job' from broadcast")
        message = self.broadcast.recv()
        self.assertEquals(message, 'new job')

    def test_command_get_configuration_should_return_dict_passed_on_setUp(self):
        self.api.send_json({'command': 'get configuration'})
        default_config = {'db': {'host': 'localhost', 'port': 27017,
                                 'database': 'pypln',
                                 'collection': 'documents',
                                 'gridfs collection': 'files',
                                 'monitoring collection': 'monitoring',},
                          'monitoring interval': 60,
                         }
        #TODO: should put configuration in another place (it should be the same
        #      default configuration from manager.py)
        if not self.api.poll(time_to_wait):
            self.fail("Didn't receive configuration from manager")
        message = self.api.recv_json()
        self.assertEquals(message, default_config)

    def test_command_add_job_should_return_a_job_id(self):
        cmd = {'command': 'add job', 'worker': 'test', 'document': 'eggs'}
        self.api.send_json(cmd)
        if not self.api.poll(time_to_wait):
            self.fail("Didn't receive 'job accepted' from manager")
        message = self.api.recv_json()
        self.assertEquals(message['answer'], 'job accepted')
        self.assertIn('job id', message)
        self.assertEquals(len(message['job id']), 32)

    def test_command_get_job_should_return_empty_if_no_job(self):
        self.api.send_json({'command': 'get job'})
        if not self.api.poll(time_to_wait):
            self.fail("Didn't receive job (None) from manager")
        message = self.api.recv_json()
        self.assertEquals(message['worker'], None)

    def test_command_get_job_should_return_a_job_after_adding_one(self):
        self.api.send_json({'command': 'add job', 'worker': 'spam',
                            'document': 'eggs'})
        if not self.api.poll(time_to_wait):
            self.fail("Didn't receive 'add job' reply")
        job = self.api.recv_json()
        self.api.send_json({'command': 'get job'})
        if not self.api.poll(time_to_wait):
            self.fail("Didn't receive job from manager")
        message = self.api.recv_json()
        self.assertEquals(message['worker'], 'spam')
        self.assertEquals(message['document'], 'eggs')
        self.assertIn('job id', message)
        self.assertEquals(len(message['job id']), 32)

    def test_finished_job_without_job_id_should_return_error(self):
        self.api.send_json({'command': 'job finished'})
        if not self.api.poll(time_to_wait):
            self.fail("Didn't receive 'syntax error' from manager")
        message = self.api.recv_json()
        self.assertEquals(message['answer'], 'syntax error')

    def test_finished_job_with_unknown_job_id_should_return_error(self):
        self.api.send_json({'command': 'job finished', 'job id': 'python rlz',
                            'duration': 0.1})
        if not self.api.poll(time_to_wait):
            self.fail("Didn't receive 'unknown job id' from manager")
        message = self.api.recv_json()
        self.assertEquals(message['answer'], 'unknown job id')

    def test_finished_job_with_correct_job_id_should_return_good_job(self):
        self.api.send_json({'command': 'add job', 'worker': 'a',
                            'document': 'b'})
        if not self.api.poll(time_to_wait):
            self.fail("Didn't receive 'add job' reply")
        message = self.api.recv_json()
        self.api.send_json({'command': 'job finished',
                            'job id': message['job id'],
                            'duration': 0.1})
        if not self.api.poll(time_to_wait):
            self.fail("Didn't receive 'good job!' from manager. "
                      "#foreveralone :-(")
        message = self.api.recv_json()
        self.assertEquals(message['answer'], 'good job!')

    def test_should_receive_job_finished_message_with_job_id_and_duration_when_a_job_finishes(self):
        self.api.send_json({'command': 'add job', 'worker': 'x',
                            'document': 'y'})
        if not self.api.poll(time_to_wait):
            self.fail("Didn't receive 'add job' reply")
        self.api.recv_json()
        if not self.broadcast.poll(time_to_wait):
            self.fail("Didn't receive 'new job' from broadcast")
        message = self.broadcast.recv()
        self.assertEquals(message, 'new job')
        self.api.send_json({'command': 'get job'})
        if not self.api.poll(time_to_wait):
            self.fail("Didn't receive 'get job' reply")
        job = self.api.recv_json()
        self.broadcast.setsockopt(zmq.SUBSCRIBE,
                                  'job finished: {}'.format(job['job id']))
        del job['worker']
        job['command'] = 'job finished'
        job['duration'] = 0.1
        self.api.send_json(job)
        if not self.broadcast.poll(time_to_wait):
            self.fail("Didn't receive 'new job' from broadcast")
        message = self.broadcast.recv()
        expected = 'job finished: {} duration: 0.1'.format(job['job id'])
        self.assertEquals(message, expected)
