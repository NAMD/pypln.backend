#!/usr/bin/env python
# coding: utf-8
#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN. You can get more information at: http://pypln.org/.
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

from logging import Logger, StreamHandler, Formatter, NullHandler
from multiprocessing import cpu_count
from sys import stdout

from pypelinin import Broker

from mongo_store import MongoDBStore


def main():
    logger = Logger('PyPLN-Broker')
    handler = StreamHandler(stdout)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - '
                          '%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    broker = Broker(api='tcp://localhost:5555',       # router API
                    broadcast='tcp://localhost:5556', # router Broadcast
                    # class that will be called to retrieve/store information
                    # to pass to/to save from worker
                    store_class=MongoDBStore,
                    logger=logger,
                    # name of the module that contain workers
                    workers='workers',
                    #TODO: string or list of modules
                    # each core will run 4 workers
                    number_of_workers=cpu_count() * 4)
    broker.start()

if __name__ == '__main__':
    main()
