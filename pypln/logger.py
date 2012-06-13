# -*- coding: utf-8 -*-
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


def make_log(name):
    """
    Sets up the logger for eah module
    :param name: Norammyl passed the name of the module so that we know where tha message comes from.
    :return: Logger object
    """
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Add the log message handler to the logger
    handler = logging.handlers.RotatingFileHandler('/tmp/pypln.log', maxBytes=200000, backupCount=1)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    #TODO: Maybe use zmq.loghandler
    return log

def make_mongolog(name):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log.addHandler(MongoHandler(host='localhost',database_name='PYPLN'))
    return log
