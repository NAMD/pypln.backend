#!/usr/bin/env python
# coding: utf-8

from logging import Logger, NullHandler
from copy import copy
import zmq


class ManagerClient(object):
    def __init__(self, logger=None, logger_name='ManagerClient'):
        self.context = zmq.Context()
        if logger is None:
            self.logger = Logger(logger_name)
            self.logger.addHandler(NullHandler())
        else:
            self.logger = logger

    def connect(self, api_host_port, broadcast_host_port):
        self.api_host_port = api_host_port
        self.broadcast_host_port = broadcast_host_port
        self.api_connection_string = 'tcp://{}:{}'.format(*api_host_port)
        self.broadcast_connection_string = \
                'tcp://{}:{}'.format(*broadcast_host_port)

        self.manager_api = self.context.socket(zmq.REQ)
        self.manager_broadcast = self.context.socket(zmq.SUB)

        self.manager_api.connect(self.api_connection_string)
        self.manager_broadcast.connect(self.broadcast_connection_string)

    def __del__(self):
        self.close_sockets()

    def close_sockets(self):
        self.manager_api.close()
        self.manager_broadcast.close()

class Worker(object):
    def __init__(self, worker_name):
        self.name = worker_name
        self.after = []

    def then(self, *after):
        self.after = after
        return self

class Pipeline(object):
    def __init__(self, pipeline, api_host_port, broadcast_host_port,
                 logger=None, logger_name='Pipeline'):
        self.client = ManagerClient(logger, logger_name)
        self.client.connect(api_host_port, broadcast_host_port)
        self.pipeline = pipeline

    def send_job(self, worker):
        job = {'command': 'add job', 'worker': worker.name,
               'document': worker.document}
        self.client.manager_api.send_json(job)
        logger.info('Sent job: {}'.format(job))
        message = self.client.manager_api.recv_json()
        logger.info('Received from Manager API: {}'.format(message))
        self.waiting[message['job id']] = worker
        subscribe_message = 'job finished: {}'.format(message['job id'])
        self.client.manager_broadcast.setsockopt(zmq.SUBSCRIBE,
                                                 subscribe_message)
        logger.info('Subscribed on Manager Broadcast to: {}'.format(subscribe_message))

    def distribute(self):
        self.waiting = {}
        for document in self.documents:
            worker = copy(self.pipeline)
            worker.document = document
            self.send_job(worker)

    def run(self, documents):
        self.documents = documents
        self.distribute()
        try:
            while True:
                try:
                    message = self.client.manager_broadcast.recv()
                except zmq.ZMQError:
                    sleep(0.1)
                    pass
                else:
                    logger.info('Received from Manager Broadcast: {}'.format(message))
                    if message.startswith('job finished: '):
                        job_id = message.split(': ')[1]
                        worker = self.waiting[job_id]
                        for next_worker in worker.after:
                            next_worker.document = worker.document
                            self.send_job(next_worker)
                        del self.waiting[job_id]
                    if not self.waiting.keys():
                        break
        except KeyboardInterrupt:
            self.client.close_sockets()


if __name__ == '__main__':
    #TODO: create main() function
    from logging import Logger, StreamHandler, Formatter
    import os
    from sys import stdout, argv
    from pymongo import Connection
    from gridfs import GridFS


    logger = Logger('Pipeline')
    handler = StreamHandler(stdout)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    connection = Connection()
    collection = connection.pypln.documents
    connection.pypln.documents.drop()
    connection.pypln.files.chunks.drop()
    connection.pypln.files.files.drop()
    W, W.__call__ = Worker, Worker.then
    my_docs = []
    if len(argv) == 1:
        for i in range(1, 11):
            text = 'The sky is blue and this is the {}th document.'.format(i)
            doc_id = collection.insert({'meta': {}, 'text': text, 'spam': 123,
                                        'eggs': 456, 'ham': 789})
            my_docs.append(str(doc_id))
        workers = W('tokenizer')(W('pos'),
                                 W('freqdist'))
    else:
        workers = W('extractor')(W('tokenizer')(W('pos'),
                                                W('freqdist')))
        gridfs = GridFS(connection.pypln, 'files')
        filenames = argv[1:]
        logger.info('Inserting files...')
        for filename in filenames:
            if os.path.exists(filename):
                logger.debug('  {}'.format(filename))
                doc_id = gridfs.put(open(filename).read(), filename=filename)
                my_docs.append(str(doc_id))

    pipeline = Pipeline(workers, ('localhost', 5555), ('localhost', 5556),
                        logger)
    pipeline.run(my_docs)
