#!/usr/bin/env python
#-*- coding:utf-8 -*-
u"""
Created on 27/04/12
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'


class SlaveDriver(object):
    """
    Class to manage work on slave nodes
    """
    def __init__(self,opts):
        """
        SlaveDriver
        :param opts: dictionary with parameters from pypln.conf
        :return:
        """
        self.localconf = opts

        context = zmq.Context(1)
        pullsock = context.socket(zmq.PULL)
        pullsock.connect("tcp://%s:%s"%(self.localconf['masteraddress'],self.localconf['pullport']))

