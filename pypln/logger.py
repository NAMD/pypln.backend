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
import ConfigParser

#TODO: change conf path to definitive  one
config = ConfigParser.ConfigParser()
config.read('../../tests/pypln.test.conf')


# Setting up the logger
def make_log(name):
    """
    Sets up the logger for eah module
    :param name: Norammyl passed the name of the module so that we know where tha message comes from.
    :return: Logger object
    """
    log = logging.getLogger(name)
    level_dict = {'debug':logging.DEBUG,'info':logging.INFO,'warning':logging.WARNING,'error':logging.ERROR}
    try:
        log.setLevel(level_dict[config.get('logging','loglevel')])
    except KeyError:
        log.setLevel(logging.INFO)
    except ConfigParser.NoSectionError:
        #TODO: this exception should be removed when false NoSectionErrors are diagnosed and eliminated
        print config._sections
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Add the log message handler to the logger
    fhandler = logging.handlers.RotatingFileHandler('/tmp/pypln.log', maxBytes=200000, backupCount=1)
    fhandler.setFormatter(formatter)
    log.addHandler(fhandler)
    log.addHandler(MongoHandler(host='localhost', database_name='PYPLN'))
    #TODO: Maybe use zmq.loghandler
    return log
