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

class DocConverterWorker(PushPullWorker):
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
        msgout = {'fail':1}
        try :
            fi = pdf.read()
            p = subprocess.Popen(['pdftotext','-q','-','-'],stdin=subprocess.PIPE,  stdout=subprocess.PIPE)
            stdout, stderr = p.communicate(input=fi)
            # Also get file Metadata
            q = subprocess.Popen(['pdfinfo','-meta','-'],stdin=subprocess.PIPE,  stdout=subprocess.PIPE)
            metadata, mderr = q.communicate(input=fi)
            metadata = self.parse_metadata(metadata)
            if not (stdout and metadata):
                msgout = {'fail':1}
            else:
                if not stderr and not mderr:
                    msgout = {'filename':pdf.filename,'text':stdout.strip(),'file_metadata':metadata,
                              'database':msg['database'],'collection':msg['collection']}
                else:
                    msgout = {'fail':1}
                    try:
                        p.kill()
                        q.kill()
                    except OSError:
                        pass
                        #process is already dead

        except ValueError:
            msgout = {'fail':1}
            try:
                p.kill()
                q.kill()
            except OSError:
                pass
                #process is already dead
        except OSError:
            msgout = {'fail':1}
            try:
                p.kill()
                q.kill()
            except OSError:
                pass
                #process is already dead

        finally:
            self.sender.send_json(msgout)
        return msgout
        # Assumes encoding is utf-8, which is not guaranteed. Although pdftotext attempts to convert to utf-8 it may not work.



    def parse_metadata(self,md):
        """
        Extracts the metadata and inserts it in a dictionary
        :param md:
        :return: dictionary with the metadata
        """
        md = md.strip().splitlines()
        d = {}
        for l in md:
            k, v = l[:l.index(':')], l[l.index(':')+1:]
            d[k.strip()] = v.strip()
        return d



if __name__=="__main__":
    # this is run when worker is spawned directly from the console
    W=DocConverterWorker()
    W()
