# -*- coding: utf-8 -*-
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
"""
Define logger infrastructure for the cluster


license: GPL v3 or later
4/30/12
"""

__docformat__ = "restructuredtext en"

import logging
import logging.handlers
from log4mongo.handlers import MongoHandler

# Setting up the logger


def make_log(name,fs=False):
    """
    Sets up the logger for each module
    :param name: pass the name of the module so that we know where tha message comes from.
    :return: Logger object
    """
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Add the log message handler to the logger
    rfhandler = logging.handlers.RotatingFileHandler('/tmp/pypln.log', maxBytes=200000, backupCount=1)
    rfhandler.setFormatter(formatter)
    if fs:
        log.addHandler(rfhandler)
    log.addHandler(MongoHandler(host='localhost',database_name='pypln'))
    #TODO: Maybe use zmq.loghandler
    return log


