#!/usr/bin/env python
# coding: utf-8

import uuid
from Queue import Queue
from logging import Logger, NullHandler
import zmq


class Manager(object):
    #TODO: add another queue for processing jobs
    #TODO: add a timeout for processing jobs (default or get it from client)
    #TODO: if processing job have timeout, remove from processing queue, add
    #      again in job_queue and announce pending job
    def __init__(self, config, logger=None, logger_name='Manager'):
        self.job_queue = Queue()
        self.pending_job_ids = []
        self.context = zmq.Context()
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

    def get_request(self):
        message = self.api.recv_json()
        self.logger.info('[API] Request: {}'.format(message))
        return message

    def reply(self, message):
        self.api.send_json(message)
        self.logger.info('[API] Reply: {}'.format(message))

    def run(self):
        self.logger.info('Entering main loop')
        try:
            while True:
                message = self.get_request()
                if 'command' not in message:
                    self.reply({'answer': 'undefined command'})
                    continue
                command = message['command']
                if command == 'get configuration':
                    self.reply(self.config)
                elif command == 'add job':
                    message['job id'] = uuid.uuid4().hex
                    del message['command']
                    self.job_queue.put(message)
                    self.pending_job_ids.append(message['job id'])
                    self.reply({'answer': 'job accepted',
                                        'job id': message['job id']})
                    self.broadcast.send('new job')
                    self.logger.info('[Broadcast] Sent "new job"')
                elif command == 'get job':
                    if self.job_queue.empty():
                        self.reply({'worker': None})
                    else:
                        job = self.job_queue.get()
                        self.reply(job)
                elif command == 'job finished':
                    if 'job id' not in message or 'duration' not in message:
                        self.reply({'answer': 'syntax error'})
                    else:
                        job_id = message['job id']
                        if job_id not in self.pending_job_ids:
                            self.reply({'answer': 'unknown job id'})
                        else:
                            self.pending_job_ids.remove(job_id)
                            self.reply({'answer': 'good job!'})
                            new_message = 'job finished: {} duration: {}'\
                                          .format(job_id, message['duration'])
                            self.broadcast.send(new_message)
                            self.logger.info('[Broadcast] Sent "new job"')
                else:
                    self.reply({'answer': 'unknown command'})
        except KeyboardInterrupt:
            self.close_sockets()

def main():
    from logging import Logger, StreamHandler, Formatter
    from sys import stdout


    logger = Logger('Manager')
    handler = StreamHandler(stdout)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - '
                          '%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    api_host_port = ('*', 5555)
    broadcast_host_port = ('*', 5556)
    config = {'db': {'host': 'localhost', 'port': 27017,
                     'database': 'pypln',
                     'collection': 'documents',
                     'gridfs collection': 'files',
                     'monitoring collection': 'monitoring'},
              'monitoring interval': 60,}
    manager = Manager(config, logger)
    manager.bind(api_host_port, broadcast_host_port)
    manager.run()


if __name__ == '__main__':
    main()
