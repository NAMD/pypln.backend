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

from sys import stdout
from logging import Logger, StreamHandler, Formatter
from pypelinin import Router


def main():
    logger = Logger('PyPLN-Router')
    handler = StreamHandler(stdout)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - '
                          '%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    api_host_port = ('*', 5555)
    broadcast_host_port = ('*', 5556)
    default_config = {'store': {'host': 'localhost', 'port': 27017,
                                'database': 'pypln',
                                'analysis_collection': 'analysis',
                                'gridfs_collection': 'files',
                                'monitoring_collection': 'monitoring',},
                      'monitoring interval': 60,
    }
    router = Router(api_host_port, broadcast_host_port, default_config, logger)
    router.start()

if __name__ == '__main__':
    main()
