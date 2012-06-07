# coding: utf-8

import unittest
import shlex
from os import unlink
from textwrap import dedent
from signal import SIGINT, SIGKILL
from time import sleep, time
from subprocess import Popen, PIPE
from multiprocessing import cpu_count
from md5 import md5
import zmq
from pymongo import Connection
from gridfs import GridFS
from psutil import Process, NoSuchProcess


time_to_wait = 150

class TestManagerBroker(unittest.TestCase):
    @classmethod
    def create_worker(cls, filename, contents):
        worker = open(filename, 'w')
        worker.write(contents)
        worker.close()
        cls.workers.append(filename)

    @classmethod
    def setUpClass(cls):
        cls.workers = []
        cls.create_worker('./pypln/workers/dummy.py', dedent('''
            __meta__ = {'from': '', 'requires': [], 'to': '', 'provides': []}
            def main(document):
                return {}
        '''))
        cls.create_worker('./pypln/workers/echo.py', dedent('''
            __meta__ = {'from': 'document', 'requires': ['key-a', 'key-b'],
                        'to': 'document', 'provides': ['key-c', 'key-d']}
            def main(document):
                return {'key-c': document['key-a'], 'key-d': document['key-b']}
        '''))
        cls.create_worker('./pypln/workers/gridfs_clone.py', dedent('''
            __meta__ = {'from': 'gridfs-file',
                        'requires': ['length', 'md5', 'name', 'upload_date',
                                     'contents'],
                        'to': 'document',
                        'provides': ['length', 'md5', 'name', 'upload_date',
                                     'contents']}
            def main(document):
                return document
        '''))
        cls.create_worker('./pypln/workers/snorlax.py', dedent('''
            from time import sleep
            __meta__ = {'from': 'document', 'requires': ['sleep-for'],
                        'to': '', 'provides': []}
            def main(document):
                sleep(document['sleep-for'])
                return {}
        '''))

        cls.config = {'db': {'host': 'localhost', 'port': 27017,
                             'database': 'pypln_test',
                             'collection': 'documents',
                             'gridfs-collection': 'files'}}
        cls.connection = Connection(cls.config['db']['host'],
                                    cls.config['db']['port'])
        cls.db = cls.connection[cls.config['db']['database']]
        cls.collection = cls.db[cls.config['db']['collection']]
        cls.gridfs = GridFS(cls.db, cls.config['db']['gridfs-collection'])

    @classmethod
    def tearDownClass(cls):
        cls.connection.drop_database(cls.config['db']['database'])
        cls.connection.close()
        for worker in cls.workers:
            unlink(worker)
            unlink(worker + 'c') # .pyc

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
        try:
            self.broker.send_signal(SIGINT)
            sleep(time_to_wait / 1000.0)
            self.broker.send_signal(SIGKILL)
            self.broker.wait()
        except OSError:
            pass

    def start_manager_sockets(self):
        self.api = self.context.socket(zmq.REP)
        self.broadcast = self.context.socket(zmq.PUB)
        self.api.bind('tcp://*:5555')
        self.broadcast.bind('tcp://*:5556')

    def close_sockets(self):
        self.api.close()
        self.broadcast.close()

    def receive_get_configuration_and_send_it_to_broker(self):
        if not self.api.poll(time_to_wait):
            self.fail("Didn't receive 'get configuration' from broker")
        message = self.api.recv_json()
        self.api.send_json(self.config)
        self.assertEquals(message, {'command': 'get configuration'})

    def receive_get_job_and_send_it_to_broker(self, job=None):
        if not self.api.poll(time_to_wait):
            self.fail("Didn't receive 'get job' from broker")
        message = self.api.recv_json()
        if job is None:
            job = {'worker': 'dummy', 'document': '1', 'job id': '2'}
        self.api.send_json(job)
        self.assertEquals(message, {'command': 'get job'})

    def broker_should_be_quiet(self):
        sleep(time_to_wait / 1000.0)
        with self.assertRaises(zmq.ZMQError):
            self.api.recv_json(zmq.NOBLOCK)

    def test_should_ask_for_configuration_on_start(self):
        self.receive_get_configuration_and_send_it_to_broker()

    def test_should_ask_for_a_job_after_configuration(self):
        self.receive_get_configuration_and_send_it_to_broker()
        self.receive_get_job_and_send_it_to_broker()

    def test_broker_should_send_get_job_just_after_manager_broadcast_new_job(self):
        self.receive_get_configuration_and_send_it_to_broker()
        self.receive_get_job_and_send_it_to_broker({'worker': None})
        self.broker_should_be_quiet()
        self.broadcast.send('new job')
        # just kidding
        self.receive_get_job_and_send_it_to_broker({'worker': None})

    def test_broker_should_send_finished_job_when_asked_to_run_dummy_worker(self):
        self.receive_get_configuration_and_send_it_to_broker()

        jobs = [{'worker': 'dummy', 'document': 'xpto'}] * 4
        finished_jobs = 0
        for i in range(3 * cpu_count()):
            if not self.api.poll(3 * time_to_wait):
                self.fail("Didn't receive 'get job' or 'finished job'")
            message = self.api.recv_json() # 'get job' or 'finished job'
            if message == {'command': 'get job'}:
                if len(jobs):
                    job = jobs.pop()
                    job['job id'] = str(i)
                else:
                    job = {'worker': None}
                self.api.send_json(job)
            elif 'command' in message and message['command'] == 'job finished':
                finished_jobs += 1
                self.api.send_json({'answer': 'good job!'})
        self.assertEquals(finished_jobs, cpu_count())
        self.broker_should_be_quiet()

    def test_broker_should_load_file_from_gridfs_and_save_what_worker_returns_to_collection(self):
        document_id = self.collection.insert({'key-a': 'spam', 'key-b': 'eggs'})
        job = {'worker': 'echo', 'document': str(document_id), 'job id': '42'}
        self.receive_get_configuration_and_send_it_to_broker()
        self.receive_get_job_and_send_it_to_broker(job)
        message = None
        for i in range(cpu_count() - 1):
            if not self.api.poll(3 * time_to_wait):
                self.fail("Didn't receive 'get job' from broker")
            msg = self.api.recv_json()
            if msg['command'] == 'job finished':
                message = msg
                self.api.send_json({'answer': 'good job!'})
                break
            else:
                self.api.send_json({'worker': None})
        if message is None:
            if not self.api.poll(3 * time_to_wait):
                self.fail("Didn't receive 'job finished' from broker")
            message = self.api.recv_json()
        self.assertIn('command', message)
        self.assertIn('job id', message)
        self.assertEquals(message['command'], 'job finished')
        self.assertEquals(message['job id'], '42')
        search_document = self.collection.find({'_id': document_id})
        self.assertEquals(search_document.count(), 1)
        document = search_document[0]
        self.assertEquals(document['key-c'], document['key-a'])
        self.assertEquals(document['key-d'], document['key-b'])

    def test_broker_should_load_and_save_document_from_and_to_collection(self):
        file_contents = 'Now is better than never.'
        filename = 'this.txt'
        document_id = self.gridfs.put(file_contents, filename=filename)
        job = {'worker': 'gridfs_clone', 'document': str(document_id),
               'job id': '42'}
        self.receive_get_configuration_and_send_it_to_broker()
        self.receive_get_job_and_send_it_to_broker(job)
        message = None
        for i in range(cpu_count() - 1):
            if not self.api.poll(3 * time_to_wait):
                self.fail("Didn't receive 'get job' from broker")
            msg = self.api.recv_json()
            if msg['command'] == 'job finished':
                message = msg
                self.api.send_json({'answer': 'good job!'})
                break
            else:
                self.api.send_json({'worker': None})
        if message is None:
            if not self.api.poll(3 * time_to_wait):
                self.fail("Didn't receive 'job finished' from broker")
            message = self.api.recv_json()
        self.assertIn('command', message)
        self.assertIn('job id', message)
        self.assertEquals(message['command'], 'job finished')
        self.assertEquals(message['job id'], '42')
        search_document = self.collection.find({'_id': document_id})
        self.assertEquals(search_document.count(), 1)
        document = search_document[0]
        gridfs_document = self.gridfs.get(document_id)
        self.assertEquals(document['name'], filename)
        self.assertEquals(document['length'], len(file_contents))
        self.assertEquals(document['md5'], md5(file_contents).hexdigest())
        self.assertEquals(document['contents'], file_contents)
        self.assertEquals(document['upload_date'],
                          gridfs_document.upload_date)

    def test_broker_should_kill_active_workers_process_when_receive_SIGINT(self):
        document_id = str(self.collection.insert({'sleep-for': 100}))
        jobs = [{'worker': 'snorlax', 'document': document_id,
                 'job id': '143'}] * cpu_count()
        self.receive_get_configuration_and_send_it_to_broker()
        for index, job in enumerate(jobs):
            job['job id'] = '143-{}'.format(index)
            self.receive_get_job_and_send_it_to_broker(job)
        sleep(cpu_count() * time_to_wait / 1000.0)
        broker_pid = self.broker.pid
        children_pid = [process.pid for process in \
                        Process(broker_pid).get_children()]
        self.assertEquals(len(children_pid), cpu_count())
        self.end_broker_process()
        with self.assertRaises(NoSuchProcess):
            broker_process = Process(broker_pid)
        for child_pid in children_pid:
            with self.assertRaises(NoSuchProcess):
                snorlax_process = Process(child_pid)

    def test_broker_should_return_time_spent_by_worker(self):
        sleep_time = 0.1
        document_id = str(self.collection.insert({'sleep-for': sleep_time}))
        job = {'worker': 'snorlax', 'document': document_id, 'job id': '143'}
        self.receive_get_configuration_and_send_it_to_broker()
        self.receive_get_job_and_send_it_to_broker(job)
        start_time = time()
        for i in range(cpu_count() - 1):
            if not self.api.poll(3 * time_to_wait):
                self.fail("Didn't receive 'get job' from broker")
            msg = self.api.recv_json()
            if msg['command'] == 'job finished':
                end_time = time()
                message = msg
                self.api.send_json({'answer': 'good job!'})
                break
            else:
                self.api.send_json({'worker': None})
        if message is None:
            if not self.api.poll(3 * time_to_wait):
                self.fail("Didn't receive 'job finished' from broker")
            message = self.api.recv_json()
            end_time = time()
        self.assertIn('duration', message)
        self.assertTrue(0 < message['duration'] < (end_time - start_time))
