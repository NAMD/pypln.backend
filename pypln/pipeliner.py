#!/usr/bin/env python
# coding: utf-8

#TODO: test it!
#TODO: in future, pipeliner could be a worker in a broker tagged as pipeliner,
#      but manager needs to support broker tags

from uuid import uuid4
from pypln.client import ManagerClient


class Worker(object):
    def __init__(self, worker_name):
        self.name = worker_name
        self.after = []

    def then(self, *after):
        self.after = after
        return self

class Pipeliner(ManagerClient):
    #TODO: should send monitoring information?
    #TODO: use et2 to create the tree/pipeline image
    #TODO: should receive and handle a 'job error' from manager when some job
    #      could not be processed (timeout, worker not found etc.)

    def __init__(self, api_host_port, broadcast_host_port, logger=None,
                 poll_time=50):
        super(Pipeliner, self).__init__()
        self.api_host_port = api_host_port
        self.broadcast_host_port = broadcast_host_port
        self.logger = logger
        self.poll_time = poll_time
        self._new_pipelines = 0
        self._messages = []
        self._pipelines = {}
        self._jobs = {}
        self.logger.info('Pipeliner started')

    def start(self):
        try:
            self.connect(self.api_host_port, self.broadcast_host_port)
            self.broadcast_subscribe('new pipeline')
            self.run()
        except KeyboardInterrupt:
            self.logger.info('Got SIGNINT (KeyboardInterrupt), exiting.')
            self.close_sockets()

    def _update_broadcast(self):
        if self.broadcast_poll(self.poll_time):
            message = self.broadcast_receive()
            self.logger.info('Received from broadcast: {}'.format(message))
            if message.startswith('new pipeline'):
                self._new_pipelines += 1
            else:
                self._messages.append(message)

    def manager_has_new_pipeline(self):
        self._update_broadcast()
        return self._new_pipelines > 0

    def ask_for_a_pipeline(self):
        self.send_api_request({'command': 'get pipeline'})
        message = self.get_api_reply()
        #TODO: if manager stops and doesn't answer, pipeliner will stop here
        if 'data' in message:
            if message['data'] is not None:
                self.logger.info('Got this pipeline: {}'.format(message))
                self._new_pipelines -= 1
                return message
        elif 'pipeline' in message and message['pipeline'] is None:
            self.logger.info('Bad bad manager, no pipeline for me.')
            return None
        else:
            self.logger.info('Ignoring malformed pipeline: {}'.format(message))
            #TODO: send a 'rejecting pipeline' request to Manager
            return None

    def get_a_pipeline(self):
        data = self.ask_for_a_pipeline()
        if data is not None:
            self.start_pipeline(data)

    def _send_job(self, worker):
        job = {'command': 'add job', 'worker': worker.name,
               'data': worker.data}
        self.logger.info('Sending new job: {}'.format(job))
        self.send_api_request(job)
        self.logger.info('Sent job: {}'.format(job))
        message = self.get_api_reply()
        self.logger.info('Received from Manager API: {}'.format(message))
        self._jobs[message['job id']] = worker
        subscribe_message = 'job finished: {}'.format(message['job id'])
        self.broadcast_subscribe(subscribe_message)
        self.logger.info('Subscribed on Manager Broadcast to: {}'\
                         .format(subscribe_message))

    def start_pipeline(self, data):
        pipeline_id = data['pipeline id']
        workers = Worker('extractor').then(Worker('tokenizer').then(Worker('pos'),
                                                                    Worker('freqdist')))
        workers.pipeline = pipeline_id
        workers.data = data['data']
        self._pipelines[pipeline_id] = [workers]
        self._send_job(workers)

    def verify_jobs(self):
        self._update_broadcast()
        new_messages = []
        for message in self._messages:
            if message.startswith('job finished: '):
                job_id = message.split(': ')[1].split(' ')[0]
                self.logger.info('Processing finished job id {}.'.format(job_id))
                worker = self._jobs[job_id]
                self._pipelines[worker.pipeline].remove(worker)
                for next_worker in worker.after:
                    next_worker.data = worker.data
                    next_worker.pipeline = worker.pipeline
                    self._pipelines[worker.pipeline].append(next_worker)
                    self._send_job(next_worker)
                del self._jobs[job_id]
                if not self._pipelines[worker.pipeline]:
                    self.send_api_request({'command': 'pipeline finished',
                                           'pipeline id': worker.pipeline})
                    self.get_api_reply()
                    #TODO: check reply
                    del self._pipelines[worker.pipeline]
                    self.logger.info('Finished pipeline {}'\
                                     .format(worker.pipeline))
                    self.get_a_pipeline()
                self.broadcast_unsubscribe(message)
        self._messages = []

    def run(self):
        self.logger.info('Entering main loop')
        self.get_a_pipeline()
        while True:
            if self.manager_has_new_pipeline():
                self.get_a_pipeline()
            self.verify_jobs()


def main():
    from logging import Logger, StreamHandler, Formatter
    from sys import stdout


    logger = Logger('Pipeliner')
    handler = StreamHandler(stdout)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - '
                          '%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    pipeliner = Pipeliner(('localhost', 5555), ('localhost', 5556),
                          logger=logger)
    pipeliner.start()

if __name__ == '__main__':
    main()
