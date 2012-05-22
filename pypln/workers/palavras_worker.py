#-*- coding:utf-8 -*-
"""
 class: palavras_worker
 connect worker to palavras (bick), and return annotation
 Author: Agnaldo L Martins (agnaldo@toptc.com.br)
"""
import os
import subprocess
import zmq
from base import PushPullWorker

context = zmq.Context()

class Palavras_worker(PushPullWorker):
   def start(self):
        # Process tasks forever
        while True:
            socks = dict(self.poller.poll())
            if self.receiver in socks and socks[self.receiver] == zmq.POLLIN:
                msg = self.receiver.recv_json()
                self.process(msg)
            if self.hear in socks and socks[self.hear] == zmq.POLLIN:
                msg = self.hear.recv_json()
                print msg
                break

   def process (msg):
       """
        Tries to convert a txt to a noted text using the cat command
        msg must be the a JSON object with the following structure: {'md5':..., 'filename':..., 'date':}

        All possibles parameters are:
            cat teste.org.txt | /opt/palavras/por.pl
            cat teste.org.txt | /opt/palavras/por.pl --dep
            cat teste.org.txt | /opt/palavras/por.pl --sem
            cat teste.org.txt | /opt/palavras/por.pl --morf
            cat teste.org.txt | /opt/palavras/por.pl --syn
            cat teste.org.txt | /opt/palavras/por.pl --sem | /opt/palavras/bin/cg2dep ptt
            cat teste.org.txt | /opt/palavras/por.pl | /opt/palavras/bin/visldep2malt
            cat teste.org.txt | /opt/palavras/por.pl | /opt/palavras/bin/visldep2malt | /opt/palavras/bin/extra2sem
            cat teste.org.txt | /opt/palavras/por.pl | /opt/palavras/bin/dep2tree_pt
            cat teste.org.txt | /opt/palavras/por.pl | perl -wnpe 's/^=//;' | /opt/palavras/bin/visl2tiger.pl | /opt/palavras/bin/extra2sem
        """
       p = subprocess.Popen(['cat', msg, '/opt/palavras/por.pl'], stdout=subprocess.PIPE)
       stdout, stderr = p.communicate()
       # Assumes encoding is utf-8 which is not guaranteed.
       # Although pdftotext attempts to convert to utf-8 it may not work.
       msgout = msg.update({'text': stdout})
       if not stderr:
           self.sender.send_unicode(msgout, encoding='utf-8')

if __name__== '__main__':
    worker = Palavras_worker()
    worker.start()
