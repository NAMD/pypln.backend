#!/usr/bin/env python
# coding: utf-8

import uuid
from Queue import Queue
from time import sleep
from logging import Logger, NullHandler
import zmq


class Manager(object):
    #TODO: add another queue for processing jobs
    #TODO: add a timeout for processing jobs (default or get it from client)
    #TODO: if processing job have timeout, remove from processing queue, add
    #      again in job_queue and announce pending job
    #TODO: get status from brokers
    def __init__(self, config, logger=None, logger_name='Manager',
                 time_to_sleep=0.1):
        self.job_queue = Queue()
        self.pending_job_ids = []
        self.context = zmq.Context()
        self.time_to_sleep = time_to_sleep
        self.config = config
        if logger is None:
            self.logger = Logger(logger_name)
            self.logger.addHandler(NullHandler())
        else:
            self.logger = logger

    def bind(self, api_host_port, broadcast_host_port):
        self.api_host_port = api_host_port
        self.broadcast_host_port = broadcast_host_port

        self.api = self.context.socket(zmq.REP)
        self.broadcast = self.context.socket(zmq.PUB)

        self.api.bind('tcp://{}:{}'.format(*self.api_host_port))
        self.broadcast.bind('tcp://{}:{}'.format(*self.broadcast_host_port))

    def close_sockets(self):
        self.api.close()
        self.broadcast.close()

    def run(self):
        try:
            while True:
                try:
                    message = self.api.recv_json(zmq.NOBLOCK)
                except zmq.ZMQError:
                    sleep(self.time_to_sleep)
                    pass
                else:
                    self.logger.info('Manager API received: {}'.format(message))
                    if 'command' not in message:
                        self.api.send_json({'answer': 'undefined command'})
                        self.logger.info('Message discarded: {}'.format(message))
                        continue
                    command = message['command']
                    if command == 'get configuration':
                        self.api.send_json(self.config)
                    elif command == 'add job':
                        message['job id'] = uuid.uuid4().hex
                        del message['command']
                        self.job_queue.put(message)
                        self.pending_job_ids.append(message['job id'])
                        self.api.send_json({'answer': 'job accepted',
                                            'job id': message['job id']})
                        self.broadcast.send('new job')
                    elif command == 'get job':
                        if self.job_queue.empty():
                            self.api.send_json({'worker': None})
                        else:
                            job = self.job_queue.get()
                            self.api.send_json(job)
                    elif command == 'finished job':
                        if 'job id' not in message:
                            self.api.send_json({'answer': 'syntax error'})
                        else:
                            job_id = message['job id']
                            if job_id not in self.pending_job_ids:
                                self.api.send_json({'answer': 'unknown job id'})
                            else:
                                self.pending_job_ids.remove(job_id)
                                self.api.send_json({'answer': 'good job!'})
                                new_message = 'job finished: {}'.format(job_id)
                                self.broadcast.send(new_message)
                    else:
                        self.api.send_json({'answer': 'unknown command'})
        except KeyboardInterrupt:
            self.close_sockets()


if __name__ == '__main__':
    #TODO: create a function main()
    from logging import Logger, StreamHandler, Formatter
    from sys import stdout


    logger = Logger('Manager')
    handler = StreamHandler(stdout)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    api_host_port = ('*', 5555)
    broadcast_host_port = ('*', 5556)
    config = {'db': {'host': 'localhost', 'port': 27017, 'database': 'pypln',
                     'collection': 'documents'}}
    manager = Manager(config, logger)
    manager.bind(api_host_port, broadcast_host_port)
    manager.run()
