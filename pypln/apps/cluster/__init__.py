# -*- coding: utf-8 -*-
__docformat__ = "restructuredtext en"

import logging
import logging.handlers

# Setting up the logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler('/tmp/pypln.log', maxBytes=200000, backupCount=1)
handler.setFormatter(formatter)
log.addHandler(handler)