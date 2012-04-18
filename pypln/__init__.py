"""
PyPLN -- Distributed text processing pipeline.
Ports:
5557: task ventilator push; worker pull port
5558: worker push port; Sink pull port
5559: Ventilators  Pub/Sub port
5560: Sinks PUB/SUB port for tasks finished
"""

from zmq.core import version
#Do some version checking
pv= [int(v) for v in version.pyzmq_version().split('.')]
zv = [int(v) for v in version.zmq_version().split('.')]
try:
    assert pv >= [2,1,7]
except AssertionError:
    print "The Version of pyzmq installed must be greater than 2.1.7"
    
try:
    assert zv >= [3,0,0]
except AssertionError:
    print "The Version of 0MQ installed must be greater than 3.0.0"

## Table of task types
TASK_TYPES = {
            1: {'name':'mimetype detection', 'worker':'mime_detect_worker', 'sink':'mimetype_sink'}, 
            2: {'name':'Encoding detection', 'worker':'enc_detect_worker', 'sink':'encoding_sink'}, 
            3: {'name':'PDF to Text Conversion', 'worker':'pdfconv_worker', 'sink':'document_sink'}, 
            }
PORTS ={
        'ventilator push':5557, 
        'worker push':5558, 
        'ventilator pub':5559, 
        'sink pub':5560, 
        }
