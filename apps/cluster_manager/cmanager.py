# -*- coding: utf-8 -*-
u"""
This executable is the manager of a pypln cluster. All tasks should be started through it and are
monitorable/controllable through it.


license: GPL v3 or later
"""
__date__ = 4 / 23 / 12
__docformat__ = "restructuredtext en"

#TODO: Complete usage docs to modules docstring

class Manager(object):
    def __init__(self, config={}):
        """
        The manager class requires no parameters  as it will try to read them from configuration files.
        If they don't exist, initializatio will fail unless provided with a config dict
        :return:
        """