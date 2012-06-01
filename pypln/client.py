#!/usr/bin/env python
# coding: utf-8

from logging import Logger, NullHandler
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


if __name__ == '__main__':
    from logging import Logger, StreamHandler, Formatter
    from sys import stdout
    from pymongo import Connection


    logger = Logger('ManagerClient')
    handler = StreamHandler(stdout)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    client = ManagerClient()
    client.connect(('localhost', 5555), ('localhost', 5556))
    time_to_sleep = 0.1

    connection = Connection()
    collection = connection.pypln.documents

    my_jobs = []
    for i in range(10):
        text = 'The sky is blue and this is the {}th document.'.format(i)
        doc_id = collection.insert({'meta': {}, 'text': text, 'spam': 123,
                                    'eggs': 456, 'ham': 789})
        client.manager_api.send_json({'command': 'add job',
                                      'worker': 'tokenizer',
                                      'document': str(doc_id)})
        message = client.manager_api.recv_json()
        logger.info('Received from Manager API: {}'.format(message))

        subscribe_message = 'job finished: {}'.format(message['job id'])
        client.manager_broadcast.setsockopt(zmq.SUBSCRIBE, subscribe_message)
        logger.info('Subscribed on Manager Broadcast to: {}'.format(subscribe_message))
        my_jobs.append(message['job id'])

    try:
        while True:
            try:
                message = client.manager_broadcast.recv()
            except zmq.ZMQError:
                sleep(time_to_sleep)
                pass
            else:
                logger.info('Received from Manager Broadcast: {}'.format(message))
                if message.startswith('job finished: '):
                    my_jobs.remove(message.split(': ')[1])
                if not my_jobs:
                    break
    except KeyboardInterrupt:
        client.close_sockets()
