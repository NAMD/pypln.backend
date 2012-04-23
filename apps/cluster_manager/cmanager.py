# -*- coding: utf-8 -*-
u"""
This executable is the manager of a pypln cluster. All tasks should be started through it and are
monitorable/controllable through it.

Cluster configuration must be specified on a config file pypln.conf
with at least the following sections:
[cluster]
nodes = x.x.x.x, x.x.x.x # list of IPs to add to PyPLN cluster

[authentication]



license: GPL v3 or later
"""
__date__ = 4 / 23 / 12
__docformat__ = "restructuredtext en"

#TODO: Complete usage docs to modules docstring

import ConfigParser

class Manager(object):
    def __init__(self, config={}):
        """
        The manager class requires no parameters  as it will try to read them from configuration files.
        If they don't exist, initialization will fail unless provided with a config dict
        :return:
        """
        if not config:
            self.config = ConfigParser.ConfigParser()
            self.config.read()
        else:
            self.config = config
    def _bootstrap_cluster(self):
        u"""
        Connect to the
        :return:
        """
