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


class WorkerPool(object):
    def __init__(self, number_of_workers):
        self.workers = []
        self.number_of_workers = number_of_workers
        for i in range(number_of_workers):
            self.workers.append(Worker())

    def __len__(self):
        return len(self.workers)

    def available(self):
        return len([True for worker in self.workers if not worker.working])

    def working(self):
        return len([True for worker in self.workers if worker.working])

    def start_job(self, job_description, data):
        for worker in self.workers:
            if not worker.working:
                break
        else:
            return False
        return worker.start_job(job_description, data)

    def end_processes(self):
        for worker in self.workers:
            worker.end()

    def kill_processes(self):
        for worker in self.workers:
            try:
                kill(worker.pid, SIGKILL)
            except OSError:
                pass
        for worker in self.workers:
            worker.process.join()

class Worker(object):
    def __init__(self):
        parent_connection, child_connection = Pipe()
        self.parent_connection = parent_connection
        self.child_connection = child_connection
        self.start_time = time()
        #TODO: is there any way to *do not* connect stdout/stderr?
        self.process = Process(target=workers.wrapper,
                               args=(child_connection, ))
        self.process.start()
        self.pid = self.process.pid
        self.working = False
        self.job_info = None

    def start_job(self, job_description, data):
        if self.working:
            return False
        message = {'command': 'execute job',
                   'worker': job_description['worker'],
                   'data': data,}
        self.parent_connection.send(message)
        self.job_info = job_description
        #TODO: should worker know about document id?
        self.job_info['start time'] = time()
        self.working = True
        return True

    def __repr__(self):
        return ('<Worker(pid={}, start_time={})>'.format(self.pid,
                self.start_time))

    def get_result(self):
        if not self.finished_job():
            return None
        result = self.parent_connection.recv()
        self.job_info = None
        self.working = False
        return result

    def finished_job(self):
        return self.parent_connection.poll()

    def end(self):
        self.parent_connection.send({'command': 'exit'})
        self.parent_connection.close()

class ManagerBroker(ManagerClient):
    #TODO: ManagerBroker must use all ManagerClient's methods to interact with
    #      Manager
    #TODO: should use pypln.stores instead of pymongo directly
    #TODO: use log4mongo
    def __init__(self, api_host_port, broadcast_host_port, logger=None,
                 logger_name='ManagerBroker', poll_time=50):
        ManagerClient.__init__(self, logger=logger, logger_name=logger_name)
        self.api_host_port = api_host_port
        self.broadcast_host_port = broadcast_host_port
        self.number_of_workers = cpu_count()
        self.poll_time = poll_time
        self.last_time_saved_monitoring_information = 0
        self.pid = getpid()
        self.logger.info('Starting worker processes')
        self.worker_pool = WorkerPool(self.number_of_workers)
        self.logger.info('Broker started')

    def request(self, message):
        self.manager_api.send_json(message)
        self.logger.info('[API] Request to manager: {}'.format(message))

    def get_reply(self):
        message = self.manager_api.recv_json()
        self.logger.info('[API] Reply from manager: {}'.format(message))
        return message

    def connect_to_database(self):
        #TODO: it should be in store
        conf = self.config['db']
        self.mongo_connection = Connection(conf['host'], conf['port'])
        self.db = self.mongo_connection[conf['database']]
        if 'username' in conf and 'password' in conf and conf['username'] and \
           conf['password']:
               self.db.authenticate(conf['username'], conf['password'])
        self.documents = self.db[conf['collection']]
        self.monitoring_collection = self.db[conf['monitoring collection']]
        self.gridfs = GridFS(self.db, conf['gridfs collection'])

    def get_configuration(self):
        self.request({'command': 'get configuration'})
        self.config = self.get_reply()

    def connect_to_manager(self):
        self.logger.info('Trying to connect to manager...')
        super(ManagerBroker, self).connect(self.api_host_port,
                                           self.broadcast_host_port)
        self.ip = get_outgoing_ip(self.api_host_port)

    def save_monitoring_information(self):
        #TODO: should we send average measures insted of instant measures of
        #      some measured variables?
        #TODO: timestamp sent should be UTC
        host_info = get_host_info()
        host_info['network']['cluster ip'] = self.ip
        broker_process = get_process_info(self.pid)
        broker_process['type'] = 'broker'
        broker_process['number of workers'] = len(self.worker_pool)
        broker_process['active workers'] = self.worker_pool.working()
        processes = [broker_process]
        for worker in self.worker_pool.workers:
            process_info = get_process_info(worker.pid)
            process_info['type'] = 'worker'
            if worker.working:
                process_info['worker'] = worker.job_info['worker']
                process_info['document id'] = \
                        ObjectId(worker.job_info['data'])
            processes.append(process_info)
            #TODO: should we send worker's process information if worker is not
            #      processing a job (not worker.working)?
        data = {'host': host_info, 'timestamp': time(), 'processes': processes}
        self.monitoring_collection.insert(data)
        self.last_time_saved_monitoring_information = time()
        self.logger.info('Saved monitoring information in MongoDB')
        self.logger.debug('  Information: {}'.format(data))

    def start(self):
        try:
            self.started_at = time()
            self.connect_to_manager()
            self.manager_broadcast.setsockopt(zmq.SUBSCRIBE, 'new job')
            self.get_configuration()
            self.connect_to_database()
            self.save_monitoring_information()
            self.run()
        except KeyboardInterrupt:
            self.logger.info('Got SIGNINT (KeyboardInterrupt), exiting.')
            self.worker_pool.end_processes()
            self.worker_pool.kill_processes()
            self.close_sockets()

    def start_job(self, job_description):
        data = {}
        worker_info = workers.available[job_description['worker']]
        worker_input = worker_info['from']
        if worker_input == 'document':
            required_fields = worker_info['requires']
            fields = set(['_id', 'meta'] + required_fields)
            object_id = ObjectId(job_description['data'])
            data = self.documents.find({'_id': object_id}, fields=fields)[0]
        elif worker_input == 'gridfs-file':
            file_data = self.gridfs.get(ObjectId(job_description['data']))
            data = {'_id': ObjectId(job_description['data']),
                    'length': file_data.length,
                    'md5': file_data.md5,
                    'name': file_data.name,
                    'upload_date': file_data.upload_date,
                    'contents': file_data.read()}
        #TODO: what if input is a corpus?

        self.worker_pool.start_job(job_description, data)
        self.logger.debug('Started job "{}" for document "{}"'\
                .format(job_description['worker'], job_description['data']))

    def get_a_job(self):
        self.logger.debug('Available workers: {}'.format(self.worker_pool.available()))
        for i in range(self.worker_pool.available()):
            self.request({'command': 'get job'})
            message = self.get_reply()
            #TODO: if manager stops and doesn't answer, broker will stop here
            if 'worker' in message and message['worker'] is None:
                break # Don't have a job, stop asking
            elif 'worker' in message and 'data' in message and \
                    message['worker'] in workers.available:
                self.start_job(message)
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

    def full_of_jobs(self):
        return len(self.worker_pool) == self.worker_pool.working()

    def should_save_monitoring_information_now(self):
        time_difference = time() - self.last_time_saved_monitoring_information
        return time_difference >= self.config['monitoring interval']

    def check_if_some_job_finished_and_do_what_you_need_to(self):
        for worker in self.worker_pool.workers:
            if not worker.finished_job():
                continue
            job_id = worker.job_info['job id']
            document_id = worker.job_info['data']
            worker_function = worker.job_info['worker']
            start_time = worker.job_info['start time']
            result = worker.get_result()
            end_time = time()
            self.logger.info('Job finished: job id={}, worker={}, '
                             'document id={}, start time={}'.format(job_id,
                    worker_function, document_id, start_time))

            worker_info = workers.available[worker_function]
            update_keys = worker_info['provides']
            for key in result.keys():
                if key not in update_keys:
                    del result[key]
            worker_input = worker_info['from']
            worker_output = worker_info['to']
            if worker_input == worker_output == 'document':
                update_data = [{'_id': ObjectId(document_id)},
                               {'$set': result}]
                self.documents.update(*update_data)
                #TODO: what if document > 16MB?
            elif worker_input == 'gridfs-file' and \
                 worker_output == 'document':
                data = {'_id': ObjectId(document_id)}
                data.update(result)
                self.documents.insert(data)
            #TODO: use safe=True (probably on pypln.stores)
            #TODO: what if we have other combinations of input/output?

            self.request({'command': 'job finished',
                          'job id': job_id,
                          'duration': end_time - start_time})
            result = self.get_reply()
            self.get_a_job()

    def run(self):
        self.get_a_job()
        self.logger.info('Entering main loop')
        while True:
            if self.should_save_monitoring_information_now():
                self.save_monitoring_information()
            if not self.full_of_jobs() and self.manager_has_job():
                self.get_a_job()
            self.check_if_some_job_finished_and_do_what_you_need_to()

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
