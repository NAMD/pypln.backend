#!/usr/bin/env python
# coding: utf-8

from multiprocessing import Process, Pipe, cpu_count
from os import kill, getpid
from time import sleep, time
from signal import SIGKILL
import zmq
from pymongo import Connection
from gridfs import GridFS
from bson.objectid import ObjectId
from pypln import workers
from pypln.client import ManagerClient
from pypln.utils import get_host_info, get_outgoing_ip, get_process_info


class Job(object):
    def __init__(self, message):
        self.job_id = message['job id']
        self.document_id = message['document']
        self.worker = message['worker']
        self.parent_connection = None
        self.child_connection = None
        self.start_time = None
        self.process = None
        self.pid = None

    def __repr__(self):
        return ('<Job(worker={}, document_id={}, job_id={}, pid={}, '
                'start_time={})>'.format(self.worker, self.document_id,
                                         self.job_id, self.pid,
                                         self.start_time))

    def start(self):
        parent_connection, child_connection = Pipe()
        self.parent_connection = parent_connection
        self.child_connection = child_connection
        #TODO: is there any way to *do not* connect stdout/stderr?
        self.process = Process(target=workers.wrapper, args=(child_connection, ))
        self.start_time = time()
        self.process.start()
        self.pid = self.process.pid

    def send(self, message):
        self.parent_connection.send(message)

    def get_result(self):
        return self.parent_connection.recv()

    def finished(self):
        return self.parent_connection.poll()

    def end(self):
        self.parent_connection.close()
        self.child_connection.close()
        self.process.join()

class ManagerBroker(ManagerClient):
    #TODO: should use pypln.stores instead of pymongo directly
    #TODO: use log4mongo
    def __init__(self, api_host_port, broadcast_host_port, logger=None,
                 logger_name='ManagerBroker', poll_time=50):
        ManagerClient.__init__(self, logger=logger, logger_name=logger_name)
        self.api_host_port = api_host_port
        self.broadcast_host_port = broadcast_host_port
        self.jobs = []
        self.max_jobs = cpu_count()
        self.poll_time = poll_time
        self.last_time_saved_monitoring_information = 0
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
        self.monitoring_collection = self.db[conf['monitoring collection']]
        self.gridfs = GridFS(self.db, conf['gridfs collection'])

    def get_configuration(self):
        self.request({'command': 'get configuration'})
        self.config = self.get_reply()

    def connect_to_manager(self):
        self.logger.info('Trying to connect to manager...')
        super(ManagerBroker, self).connect(self.api_host_port,
                                           self.broadcast_host_port)

    def save_monitoring_information(self):
        #TODO: should we send average measures insted of instant measures of
        #      some measured variables?
        ip = get_outgoing_ip(self.api_host_port)
        host_info = get_host_info()
        host_info['network']['cluster ip'] = ip
        broker_process = get_process_info(getpid())
        broker_process['type'] = 'broker'
        broker_process['active workers'] = len(self.jobs)
        processes = [broker_process]
        for job in self.jobs:
            process = get_process_info(job.pid)
            if process is not None: # worker process not finished yet
                process['worker'] = job.worker
                process['document id'] = ObjectId(job.document_id)
                process['type'] = 'worker'
                processes.append(process)
        data = {'host': host_info, 'timestamp':time(), 'processes': processes}
        self.monitoring_collection.insert(data)
        self.last_time_saved_monitoring_information = time()
        self.logger.info('Saved monitoring information in MongoDB')
        self.logger.debug('  Information: {}'.format(data))

    def start(self):
        self.started_at = time()
        self.connect_to_manager()
        self.manager_broadcast.setsockopt(zmq.SUBSCRIBE, 'new job')
        self.get_configuration()
        self.connect_to_database()
        self.save_monitoring_information()
        self.run()

    def start_job(self, job):
        worker_input = workers.available[job.worker]['from']
        data = {}
        if worker_input == 'document':
            required_fields = workers.available[job.worker]['requires']
            fields = set(['_id', 'meta'] + required_fields)
            data = self.collection.find({'_id': ObjectId(job.document_id)},
                                        fields=fields)[0]
        elif worker_input == 'gridfs-file':
            file_data = self.gridfs.get(ObjectId(job.document_id))
            data = {'_id': ObjectId(job.document_id),
                    'length': file_data.length,
                    'md5': file_data.md5,
                    'name': file_data.name,
                    'upload_date': file_data.upload_date,
                    'contents': file_data.read()}
        #TODO: what if input is a corpus?

        job.start()
        job.send((job.worker, data))
        self.logger.debug('Started worker "{}" for document "{}" (PID: {})'\
                          .format(job.worker, job.document_id,
                                  job.pid))

    def get_a_job(self):
        for i in range(self.max_jobs - len(self.jobs)):
            self.request({'command': 'get job'})
            message = self.get_reply()
            #TODO: if manager stops and doesn't answer, broker will stop here
            if 'worker' in message and message['worker'] is None:
                break # Don't have a job, stop asking
            elif 'worker' in message and 'document' in message and \
                    message['worker'] in workers.available:
                job = Job(message)
                self.jobs.append(job)
                self.start_job(job)
            else:
                self.logger.info('Ignoring malformed job: {}'.format(message))
                #TODO: send a 'rejecting job' request to Manager

    def manager_has_job(self):
        if self.manager_broadcast.poll(self.poll_time):
            message = self.manager_broadcast.recv()
            self.logger.info('[Broadcast] Received from manager: {}'\
                             .format(message))
            #TODO: what if broker subscribe to another thing?
            return True
        else:
            return False

    def finished_jobs(self):
        return [job for job in self.jobs if job.finished()]

    def full_of_jobs(self):
        return len(self.jobs) >= self.max_jobs

    def kill_processes(self):
        for job in self.jobs:
            try:
                kill(job.pid, SIGKILL)
            except OSError:
                pass

    def should_save_monitoring_information_now(self):
        time_difference = time() - self.last_time_saved_monitoring_information
        return time_difference >= self.config['monitoring interval']

    def run(self):
        self.logger.info('Entering main loop')
        try:
            self.get_a_job()
            while True:
                if self.should_save_monitoring_information_now():
                    self.save_monitoring_information()
                if not self.full_of_jobs() and self.manager_has_job():
                    self.get_a_job()
                for job in self.finished_jobs():
                    result = job.get_result()
                    job.end()
                    end_time = time()
                    self.logger.info('Job finished: {}'.format(job))
                    update_keys = workers.available[job.worker]['provides']
                    for key in result.keys():
                        if key not in update_keys:
                            del result[key]
                    worker_input = workers.available[job.worker]['from']
                    worker_output = workers.available[job.worker]['to']
                    if worker_input == worker_output == 'document':
                        update_data = [{'_id': ObjectId(job.document_id)},
                                       {'$set': result}]
                        self.collection.update(*update_data)
                        #TODO: what if document > 16MB?
                    elif worker_input == 'gridfs-file' and \
                         worker_output == 'document':
                        data = {'_id': ObjectId(job.document_id)}
                        data.update(result)
                        self.collection.insert(data)
                    #TODO: use safe=True (probably on pypln.stores)
                    #TODO: what if we have other combinations of input/output?
                    self.request({'command': 'job finished',
                                  'job id': job.job_id,
                                  'duration': end_time - job.start_time})
                    result = self.get_reply()
                    self.jobs.remove(job)
                    self.get_a_job()
        except KeyboardInterrupt:
            self.logger.info('Got SIGNINT (KeyboardInterrupt), exiting.')
            self.close_sockets()
            self.kill_processes()

def main():
    from logging import Logger, StreamHandler, Formatter
    from sys import stdout


    logger = Logger('ManagerBroker')
    handler = StreamHandler(stdout)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - '
                          '%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    broker = ManagerBroker(('localhost', 5555), ('localhost', 5556),
                           logger=logger)
    broker.start()


if __name__ == '__main__':
    main()
