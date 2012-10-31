#!/usr/bin/env python
# coding: utf-8
#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN.
#
# PyPLN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPLN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPLN.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import sys
from logging import Logger, StreamHandler, Formatter
from pymongo import Connection
from gridfs import GridFS
from pypln.client import ManagerClient


def main():
    if len(sys.argv) == 1:
        print('ERROR: use: {} <file-to-add-1[ file-to-add-2[ ...]]>'\
              .format(sys.argv[0]))
        exit(1)

    logger = Logger('Manager')
    handler = StreamHandler(sys.stdout)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - '
                          '%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info('Connecting to Manager...')
    client = ManagerClient()
    client.connect(('localhost', 5555), ('localhost', 5556))

    logger.info('Getting configuration and connecting to MongoDB...')
    client.send_api_request({'command': 'get configuration'})
    conf = client.get_api_reply()
    connection = Connection(host=conf['db']['host'], port=conf['db']['port'])
    database = connection[conf['db']['database']]
    gridfs = GridFS(database, collection=conf['db']['gridfs_collection'])

    logger.info('Inserting files...')
    document_ids = []
    for filename in sys.argv[1:]:
        logger.info('  {}'.format(filename))
        fp = open(filename, 'r')
        contents = fp.read()
        fp.close()
        document_ids.append(gridfs.put(contents, filename=filename))

    logger.info('Creating pipelines...')
    pipeline_ids = []
    for index, document_id in enumerate(document_ids):
        pipeline = {'id': str(index), '_id': str(document_id)}
        client.send_api_request({'command': 'add pipeline', 'data': pipeline})
        logger.info('Sent pipeline: {}'.format(pipeline))
        reply = client.get_api_reply()
        logger.info('Received reply: {}'.format(reply))
        subscribe_message = 'pipeline finished: {}'.format(reply['pipeline id'])
        client.broadcast_subscribe(subscribe_message)
        pipeline_ids.append(reply['pipeline id'])

    try:
        while True:
            message = client.broadcast_receive()
            logger.info('Received from manager broadcast: {}'.format(message))
            if message.startswith('pipeline finished: '):
                pipeline_id = message.split(': ')[1]
                if pipeline_id in pipeline_ids:
                    pipeline_ids.remove(pipeline_id)
                if not pipeline_ids:
                    break
    except KeyboardInterrupt:
        client.close_sockets()


if __name__ == '__main__':
    main()
