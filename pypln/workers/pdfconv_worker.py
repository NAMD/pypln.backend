#-*- coding:utf-8 -*-
"""
PDF to text conversion worker
"""
__docformat__ = "restructuredtext en"

import subprocess
import zmq
from base import PushPullWorker
from pypln.stores import filestor

context = zmq.Context()

class PDFConverterWorker(PushPullWorker):
    """
    Worker to extract text from PDF files
    Expects to receive  messages with the following format:
    {'md5':..., 'filename':..., 'date':} or {'jobid':n}
    """
                
    def process(self,msg):
        """
        Tries to convert a pdf to a text file using the unix command 
        pdftotext.
        msg must be the a JSON object with the following structure: {'md5':..., 'filename':..., 'date':}
        """
        gridfs = filestor.FS(msg['database'],msg['collection'])
        pdf= gridfs.fs.get_last_version(md5=msg['md5'])
#        print msg['md5']
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
                msgout = {'filename':pdf.filename,'text':stdout.strip(),'database':msg['database'],'collection':msg['collection']} #stripping to remove non-printing characters
                self.sender.send_json(msgout)
            else:
                self.sender.send_json({'fail':1})
                p.kill()



if __name__=="__main__":
    # this is run when worker is spawned directly from the console
    W=PDFConverterWorker()
    W()
