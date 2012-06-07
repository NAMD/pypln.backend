#!/usr/bin/env python
# coding: utf-8

import socket
from multiprocessing import Process, Pipe, cpu_count
from os import kill, getpid
from time import sleep, time
from signal import SIGKILL
import zmq
from pymongo import Connection
from gridfs import GridFS
from bson.objectid import ObjectId
from client import ManagerClient
import workers


class ManagerBroker(ManagerClient):
    #TODO: should use pypln.stores instead of pymongo directly
    #TODO: send stats to MongoDB
    #TODO: use log4mongo
    def __init__(self, api_host_port, broadcast_host_port, logger=None,
                 logger_name='ManagerBroker', time_to_sleep=0.1):
        ManagerClient.__init__(self, logger=logger, logger_name=logger_name)
        self.api_host_port = api_host_port
        self.broadcast_host_port = broadcast_host_port
        self.jobs = []
        self.max_jobs = cpu_count()
        self.time_to_sleep = 0.1
        self.logger.info('Broker started')

    def request(self, message):
        self.manager_api.send_json(message)
        self.logger.info('[API] Request to manager: {}'.format(message))

    def get_reply(self):
        message = self.manager_api.recv_json()
        self.logger.info('[API] Reply from manager: {}'.format(message))
        return message

    def connect_to_database(self):
        conf = self.config['db']
        self.mongo_connection = Connection(conf['host'], conf['port'])
        self.db = self.mongo_connection[conf['database']]
        if 'username' in conf and 'password' in conf and conf['username'] and \
           conf['password']:
               self.db.authenticate(conf['username'], conf['password'])
        self.collection = self.db[conf['collection']]
        self.hosts_collection = self.db[conf['hosts-collection']]
        self.gridfs = GridFS(self.db, conf['gridfs-collection'])

    def get_local_ip_and_port(self):
        raw_socket = socket.socket(socket.AF_INET)
        raw_socket.connect(self.api_host_port)
        data = raw_socket.getsockname()
        raw_socket.close()
        return data

    def insert_host_information(self):
        ip, local_port = self.get_local_ip_and_port()
        self.hosts_collection.insert({'type': 'broker',
                                      'ip': ip,
                                      'local_port': local_port,
                                      'pid': getpid(),
                                      'timestamp': time()})

    def get_configuration(self):
        self.request({'command': 'get configuration'})
        self.config = self.get_reply()

    def connect_to_manager(self):
        self.logger.info('Trying to connect to manager...')
        super(ManagerBroker, self).connect(self.api_host_port,
                                           self.broadcast_host_port)

    def start(self):
        self.connect_to_manager()
        self.get_configuration()
        self.connect_to_database()
        self.insert_host_information()
        self.manager_broadcast.setsockopt(zmq.SUBSCRIBE, 'new job')
        self.run()

    def start_job(self, job):
        if 'worker' not in job or 'document' not in job or \
           job['worker'] not in workers.available:
            self.logger.info('Rejecting job: {}'.format(job))
            #TODO: send a 'rejecting job' request to Manager
            return
        worker_input = workers.available[job['worker']]['from']
        data = {}
        if worker_input == 'document':
            required_fields = workers.available[job['worker']]['requires']
            fields = set(['meta'] + required_fields)
            data = self.collection.find({'_id': ObjectId(job['document'])},
                                        fields=fields)[0]
        elif worker_input == 'gridfs-file':
            file_data = self.gridfs.get(ObjectId(job['document']))
            data = {'length': file_data.length,
                    'md5': file_data.md5,
                    'name': file_data.name,
                    'upload_date': file_data.upload_date,
                    'contents': file_data.read()}
        #TODO: what if input is a corpus?
        parent_connection, child_connection = Pipe()
        process = Process(target=workers.wrapper, args=(child_connection, ))
        #TODO: is there any way to *do not* connect stdout/stderr?
        process.start()
        job['start time'] = time()
        parent_connection.send((job['worker'], data))
        job['process'] = process
        job['parent_connection'] = parent_connection
        job['child_connection'] = child_connection
        self.logger.debug('Started worker "{}" for document "{}" (PID: {})'\
                          .format(job['worker'], job['document'], process.pid))

    def get_a_job(self):
        for i in range(self.max_jobs - len(self.jobs)):
            self.request({'command': 'get job'})
            message = self.get_reply()
            #TODO: if manager stops and doesn't answer, broker will stop here
            if 'worker' in message:
                if message['worker'] is None:
                    break # Don't have a job, stop asking
                else:
                    self.jobs.append(message)
                    self.start_job(message)
            else:
                self.logger.info('Ignoring malformed job: {}'.format(message))

    def manager_has_job(self):
        if self.manager_broadcast.poll(self.time_to_sleep):
            message = self.manager_broadcast.recv()
            self.logger.info('[Broadcast] Received from manager: {}'\
                             .format(message))
            #TODO: what if broker subscribe to another thing?
            return True
        else:
            return False

    def finished_jobs(self):
        return [job for job in self.jobs if job['parent_connection'].poll()]

    def full_of_jobs(self):
        return len(self.jobs) >= self.max_jobs

    def kill_processes(self):
        for job in self.jobs:
            try:
                kill(job['process'].pid, SIGKILL)
            except OSError:
                pass

    def run(self):
        self.logger.info('Entering main loop')
        try:
            self.get_a_job()
            while True:
                if not self.full_of_jobs() and self.manager_has_job():
                    self.get_a_job()
                for job in self.finished_jobs():
                    result = job['parent_connection'].recv()
                    job['parent_connection'].close()
                    job['child_connection'].close()
                    job['process'].join()
                    end_time = time()
                    self.logger.info('Job finished: {}'.format(job))
                    update_keys = workers.available[job['worker']]['provides']
                    for key in result.keys():
                        if key not in update_keys:
                            del result[key]
                    worker_input = workers.available[job['worker']]['from']
                    worker_output = workers.available[job['worker']]['to']
                    if worker_input == worker_output == 'document':
                        self.collection.update({'_id': ObjectId(job['document'])},
                                               {'$set': result})
                    elif worker_input == 'gridfs-file' and \
                         worker_output == 'document':
                        data = {'_id': ObjectId(job['document'])}
                        data.update(result)
                        self.collection.insert(data)
                    #TODO: safe=True
                    #TODO: what if we have other combinations of input/output?
                    self.request({'command': 'job finished',
                                  'job id': job['job id'],
                                  'duration': end_time - job['start time']})
                    result = self.get_reply()
                    self.jobs.remove(job)
                    self.get_a_job()
        except KeyboardInterrupt:
            self.logger.info('Got SIGNINT (KeyboardInterrupt), exiting.')
            self.close_sockets()
            self.kill_processes()


if __name__ == '__main__':
    #TODO: create a function main()
    from logging import Logger, StreamHandler, Formatter
    from sys import stdout


    logger = Logger('ManagerBroker')
    handler = StreamHandler(stdout)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    broker = ManagerBroker(('localhost', 5555), ('localhost', 5556),
                           logger=logger)
    broker.start()
