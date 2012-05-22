#-*- coding:utf-8 -*-
"""
Text parsing worker
"""

import subprocess
import zmq
from base import PushPullWorker
from pypln.stores import filestor

context = zmq.Context()

class ParserWorker(PushPullWorker):
    """
    Worker to parse text generating
    Expects to receive  messages with the following format:
    {'idlist':[...]} or {'jobid':n}
    """
    def start(self):
        # Process tasks forever
        # print self.pid,  " starting"
        msgproc = 0
        while True:
            socks = dict(self.poller.poll())
            if self.receiver in socks and socks[self.receiver] == zmq.POLLIN:
                msg = self.receiver.recv_json()
                if 'jobid' in msg: # startup message
                    # print "starting job %s"%msg['jobid']
                    self.sender.send_json({'fail':1})
                else:
                    self.process(msg)
                msgproc += 1
            if self.hear in socks and socks[self.hear] == zmq.POLLIN:
                msg = self.hear.recv()
                # print self.pid, " Done after processing %s messages"%msgproc
                break


    def process(self,msg):
        """
        Tries to convert a pdf to a text file using the unix command
        pdftotext.
        msg must be the a JSON object with the following structure: {'md5':..., 'filename':..., 'date':}
        """
        pdf = filestor.fs.get_last_version(md5=msg['text'])
        try :
            p = subprocess.Popen(['pdftotext','-q','-','-'],stdin=subprocess.PIPE,  stdout=subprocess.PIPE)
            stdout, stderr = p.communicate(input=pdf.read())
        except OSError:
            p.kill()
            self.sender.send_json({'fail':1})
            return
        # Assumes encoding is utf-8 which is not guaranteed. Although pdftotext attempts to convert to utf-8 it may not work.
        if not stdout:
            self.sender.send_json({'fail':1})
        else:
            if not stderr:
                msgout = {'filename':pdf.filename,'text':stdout.strip()} #stripping to remove non-printing characters
                self.sender.send_json(msgout)
            else:
                self.sender.send_json({'fail':1})
                p.kill()



if __name__=="__main__":
    # this is run when worker is spawned directly from the console
    W=PDFConverterWorker()
    W.start()
