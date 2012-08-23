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
    #TODO: validate all received data (types, keys etc.)
    #TODO: handle 'job failed' messages
    def __init__(self, api_host_port, broadcast_host_port, config, logger=None,
                 logger_name='Manager'):
        self.job_queue = Queue()
        self.pipeline_queue = Queue()
        #TODO: should persist jobs and recover in case of failure
        self.pending_job_ids = []
        self.pending_pipeline_ids = []
        self.context = zmq.Context()
        self.config = config
        if logger is None:
            self.logger = Logger(logger_name)
            self.logger.addHandler(NullHandler())
        else:
            self.logger = logger
        self.api_host_port = api_host_port
        self.broadcast_host_port = broadcast_host_port

    def bind(self):
        self.api = self.context.socket(zmq.REP)
        self.broadcast = self.context.socket(zmq.PUB)
        self.api.linger = 0
        self.broadcast.linger = 0
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

    def start(self):
        try:
            self.bind()
            self.run()
        except KeyboardInterrupt:
            self.logger.info('Got SIGNINT (KeyboardInterrupt), exiting.')
            self.close_sockets()

    def run(self):
        self.logger.info('Entering main loop')
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
                        self.logger.info('[Broadcast] Sent: {}'\
                                         .format(new_message))
            elif command == 'add pipeline':
                pipeline_id = uuid.uuid4().hex
                message['pipeline id'] = pipeline_id
                del message['command']
                self.pipeline_queue.put(message)
                self.pending_pipeline_ids.append(pipeline_id)
                self.reply({'answer': 'pipeline accepted',
                            'pipeline id': pipeline_id})
                self.broadcast.send('new pipeline')
                self.logger.info('[Broadcast] Sent "new pipeline"')
            elif command == 'get pipeline':
                if self.pipeline_queue.empty():
                    self.reply({'pipeline': None})
                else:
                    pipeline = self.pipeline_queue.get()
                    self.reply(pipeline)
            elif command == 'pipeline finished':
                if 'pipeline id' not in message:
                    self.reply({'answer': 'syntax error'})
                else:
                    pipeline_id = message['pipeline id']
                    if pipeline_id not in self.pending_pipeline_ids:
                        self.reply({'answer': 'unknown pipeline id'})
                    else:
                        self.pending_pipeline_ids.remove(pipeline_id)
                        self.reply({'answer': 'good job!'})
                        new_message = 'pipeline finished: {}'\
                                      .format(pipeline_id)
                        self.broadcast.send(new_message)
                        self.logger.info('[Broadcast] Sent: {}'\
                                         .format(new_message))
            else:
                self.reply({'answer': 'unknown command'})

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
    default_config = {'db': {'host': 'localhost', 'port': 27017,
                             'database': 'pypln',
                             'analysis_collection': 'analysis',
                             'gridfs_collection': 'files',
                             'monitoring_collection': 'monitoring',},
                      'monitoring interval': 60,
    }
    manager = Manager(api_host_port, broadcast_host_port, default_config,
                      logger)
    manager.start()

if __name__ == '__main__':
    main()
