#-*- coding:utf-8 -*-
"""
Created on 13/06/12
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'

from pypln.logger import make_log

log = make_log("TEST")

for i in xrange(30000):
    log.info("Information Message")
    log.debug("Debug Message")
    log.error("Error message")
    log.warning("Warning message")
