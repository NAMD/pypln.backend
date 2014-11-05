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

import ConfigParser
from sys import stdout
from logging import Logger, StreamHandler, Formatter
import os

from pypelinin import Router

def get_store_config():
    config_filename = os.path.expanduser('~/.pypln_store_config')
    defaults = {'host': 'localhost',
                'port': '27017',
                'database': 'pypln',
                'analysis_collection': 'analysis',
                'gridfs_collection': 'files',
                'monitoring_collection': 'monitoring',
    }
    config = ConfigParser.ConfigParser(defaults=defaults)
    config.add_section('store')
    config.read(config_filename)
    store_config = dict(config.items('store'))
    # The database port needs to be an integer, but ConfigParser will treat
    # everything as a string unless you use the specific method to retrieve the
    # value.
    store_config['port'] = config.getint('store', 'port')
    return store_config


def main():
    logger = Logger('PyPLN-Router')
    handler = StreamHandler(stdout)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - '
                          '%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    api_host_port = ('*', 5555)
    broadcast_host_port = ('*', 5556)
    default_config = {'store': get_store_config(),
                      'monitoring interval': 60,
    }
    router = Router(api_host_port, broadcast_host_port, default_config, logger)
    router.start()

if __name__ == '__main__':
    main()
