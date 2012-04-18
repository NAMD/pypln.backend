#-*- coding:utf-8 -*-
"""
Test module for testing worker spawning and killing
workers and sinks
"""
import unittest
from servers.ventilator import Ventilator
from workers.dummy_worker import DummyWorker
from sinks.dummy_sink import DummySink
from multiprocessing import Process
from subprocess import Popen
import time

class testWorkerModules(unittest.TestCase):
    def setUp(self):
        #start a ventilator
        self.V = Ventilator()
        self.nw = 4
        #spawn 4 workers
        self.ws = [Popen(['python', 'workers/dummy_worker.py'], stdout=None) for i in range(self.nw)]
        #~ self.ws = []
        #~ for i in range(self.nw):
            #~ w = DummyWorker2
            #~ P = Process(target=w)
            #~ P.start()
            #~ self.ws.append(P)

        #spawn a sink
        self.sink = Popen(['python', 'sinks/dummy_sink.py'], stdout=None)


        # wait for workers and sinks to connect
        time.sleep(1)

    def test_send_json(self):
        '''
        Pushing json with unicode through workers to sinks.
        '''

        self.V.push_load([{'text':u'são joão'} for i in xrange(80)])
        time.sleep(2)
        #[p.wait() for p in self.ws]#wait for the workers to terminate
        wsr = [p.poll() for p in self.ws]
        time.sleep(1)
        self.sink.wait()
        sr = self.sink.returncode
        self.assertEqual([0]*self.nw, wsr)
        self.assertEqual(0, sr)

    def tearDown(self):
        pass
#        try:
#            self.sink.kill()
#            #tries to kill worker processes if they are still active
#            [p.kill() for p in self.ws]
#        except OSError as e:
#            print "No processes left to kill", e

class testWorkerAsSubprocesses(unittest.TestCase):
    def setUp(self):
        #start a ventilator
        self.V = Ventilator(pushport=5561,pubport=5562,subport=5563)
        self.nw = 4
        #spawn 4 workers
        self.ws = [Process(target=DummyWorker(pushport=5564,pullport=5561,subport=5563)) for i in range(self.nw)]
        [p.start() for p in self.ws]


        #spawn a sink
        self.sink = Process(target=DummySink(pullport=5564,pubport=5563,subport=5562))
        self.sink.start()


        # wait for workers and sinks to connect
        time.sleep(1)

    def test_send_json(self):
        '''
        Pushing json with unicode through workers to sinks.
        '''

        self.V.push_load([{'text':u'são joão'} for i in xrange(80)])
        time.sleep(1)



    def tearDown(self):
        pass
#        try:
#            self.sink.join()
#            #tries to kill worker processes if they are still active
#            [p.join() for p in self.ws]
#        except OSError as e:
#            print e

if __name__ == '__main__':
    unittest.main()
