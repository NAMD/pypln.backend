#!/usr/bin/env python
# coding: utf-8

from time import sleep
from multiprocessing import Process, Queue, cpu_count
import zmq
from pymongo import Connection
from bson.objectid import ObjectId
from client import ManagerClient
import workers


class ManagerBroker(ManagerClient):
    #TODO: send stats to MongoDB
    #TODO: use log4mongo
    def __init__(self, logger=None, logger_name='ManagerBroker',
                 time_to_sleep=0.1):
        ManagerClient.__init__(self, logger=logger, logger_name=logger_name)
        self.jobs = []
        self.max_jobs = cpu_count()
        self.time_to_sleep = 0.1

    def connect_to_database(self):
        conf = self.config['db']
        self.mongo_connection = Connection(conf['host'], conf['port'])
        self.db = self.mongo_connection[conf['database']]
        if 'username' in conf and 'password' in conf and conf['username'] and \
           conf['password']:
               self.db.authenticate(conf['username'], conf['password'])
        self.collection = self.db[conf['collection']]

    def get_configuration(self):
        self.manager_api.send_json({'command': 'get configuration'})
        self.config = self.manager_api.recv_json()
        self.logger.info('Got configuration from Manager')
        self.connect_to_database()
        self.logger.debug('Configuration received: {}'.format(self.config))

    def connect(self, api_host_port, broadcast_host_port):
        super(ManagerBroker, self).connect(api_host_port, broadcast_host_port)
        self.get_configuration()
        self.manager_broadcast.setsockopt(zmq.SUBSCRIBE, 'new job')

    def start_job(self, job):
        if 'worker' not in job or 'document' not in job or \
           job['worker'] not in workers.available:
            self.logger.info('Rejecting job: {}'.format(job))
            #TODO: send a 'rejecting job' request to Manager
            return
        self.logger.debug('Starting worker "{}" for document "{}"'.format(job['worker'], job['document']))
        worker_input = workers.available[job['worker']]['input']
        if worker_input == 'document':
            required_fields = workers.available[job['worker']]['requires']
            fields = set(['meta'] + required_fields)
            #TODO: add option to get from GridFS
            contents = self.collection.find({'_id': ObjectId(job['document'])},
                                            fields=fields)[0]
        elif worker_input == 'file':
            file_data = self.gridfs.get(ObjectId(job['document']))
            contents = {'length': file_data.length, 'md5': file_data.md5,
                        'name': file_data.name,
                        'upload_date': file_data.upload_date,
                        'contents': file_data.read()}
        #TODO: what if input is a corpus?
        queue = Queue()
        queue.put(job['worker'])
        queue.put(contents)
        process = Process(target=workers.wrapper, args=(queue, ))
        job['queue'] = queue
        job['process'] = process
        process.start()
        self.logger.info('Worker started')

    def get_a_job(self):
        for i in range(self.max_jobs - len(self.jobs)):
            self.manager_api.send_json({'command': 'get job'})
            message = self.manager_api.recv_json()
            self.logger.info('Received from Manager API: {}'.format(message))
            if message['worker'] is not None:
                self.jobs.append(message)
                self.start_job(message)
            else:
                break

    def manager_has_job(self):
        try:
            message = self.manager_broadcast.recv(zmq.NOBLOCK)
        except zmq.ZMQError:
            return False
        else:
            self.logger.info('Received from Manager Broadcast: {}'.format(message))
            return True

    def finished_jobs(self):
        return [job for job in self.jobs if job['queue'].qsize() > 2]

    def full_of_jobs(self):
        return len(self.jobs) >= self.max_jobs

    def run(self):
        try:
            self.get_a_job()
            while True:
                if not self.full_of_jobs() and self.manager_has_job():
                    self.logger.info('Trying to get a new job...')
                    self.get_a_job()
                for job in self.finished_jobs():
                    job['process'].join()
                    self.logger.info('Job finished: {}'.format(job))
                    result = job['queue'].get()
                    update_keys = workers.available[job['worker']]['provides']
                    for key in result.keys():
                        if key not in update_keys:
                            del result[key]
                    self.collection.update({'_id': ObjectId(job['document'])},
                                           {'$set': result})
                    #TODO: safe=True
                    self.manager_api.send_json({'command': 'finished job',
                                                'job id': job['job id'],})
                    result = self.manager_api.recv_json()
                    self.logger.info('Result: {}'.format(result))
                    self.jobs.remove(job)
                    self.logger.info('Job removed')
                    self.get_a_job()
                sleep(self.time_to_sleep)
        except KeyboardInterrupt:
            self.close_sockets()


if __name__ == '__main__':
    #TODO: create a function main()
    from logging import Logger, StreamHandler, Formatter
    from sys import stdout


    logger = Logger('ManagerBroker')
    handler = StreamHandler(stdout)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    broker = ManagerBroker(logger=logger)
    broker.connect(('localhost', 5555), ('localhost', 5556))
    broker.run()
