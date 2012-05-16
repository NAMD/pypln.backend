#-*- coding:utf-8 -*-
"""
PDF to text conversion worker
"""
__docformat__ = "restructuredtext en"

import subprocess
import zmq
from base import PushPullWorker
from pypln.stores import filestor
from gridfs.errors import NoFile

context = zmq.Context()

class DocConverterWorker(PushPullWorker):
    """
    Worker to extract text from PDF, text, and html files
    Expects to receive  messages with the following format:
    {'md5':..., 'filename':..., 'date':,'mimetype':...} or {'jobid':n}
    """
                
    def process(self,msg):
        """
        Tries to convert a pdf to a text file using the unix command 
        pdftotext.
        msg must be the a JSON object with the following structure: {'md5':..., 'filename':..., 'date':}
        """
        gridfs = filestor.FS(msg['database'])
        try:
            fileobject = gridfs.fs.get_last_version(md5=msg['md5'])
            msgout = {'fail':1}
            if msg['mimetype'] == "application/pdf":
                msgout = self.extract_pdf(fileobject,msg)
            elif msg['mimetype'] == "text/plain":
                msgout = self.extract_txt_plain(fileobject,msg)
            elif msg['mimetype'] == "text/html":
                msgout = self.extract_txt_html(fileobject,msg)
            else:
                print "mimetype %s not recognized"%msg['mimetype']
        except NoFile:
            msgout = {'fail':1}

        msgout['mimetype'] = msg['mimetype']
        self.sender.send_json(msgout)
        return msgout
        # Assumes encoding is utf-8, which is not guaranteed. Although pdftotext attempts to convert to utf-8 it may not work.

    def extract_pdf(self, fileobj,msg):
        """
        Extract text from files of the application/pdf mmimetype
        :param fileobj: file object
        :return: msgout dictionary
        """
        try :
            fi = fileobj.read()
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
                    msgout = {'filename':fileobj.filename,'text':stdout.strip(),'file_metadata':metadata,
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

        return msgout

    def extract_txt_plain(self, fileobj,msg):
        """
        Extract text from files of the txt/plain mmimetype
        :param fileobj: file object
        :return: msgout dictionary
        """
        print "==> extracting text"
        text = fileobj.read()
        msgout = {'filename':fileobj.filename,'text':text.strip(),'database':msg['database'],'collection':msg['collection']}
        return msgout

    def extract_txt_html(self, fileobj,msg):
        """
        Extract text from files of the txt/html mmimetype
        :param fileobj: file object
        :return: msgout dictionary
        """
        print "==> extracting html"
        text = fileobj.read()
        try :
            p1 = subprocess.Popen(["html2text"], stdin=subprocess.PIPE,stdout=subprocess.PIPE)
            p2 = subprocess.Popen(["recode", "UTF-8"],stdin=p1.stdout, stdout=subprocess.PIPE)
            p1.communicate(input=text)
            p1.stdout.close() # Allow p1 to receive a SIGPIPE if p2 exits.
#            stdout = subprocess.check_output('html2text | recode UTF-8',stdin=fileobj,shell=True)
            stdout, stderr = p2.communicate()
            if not stdout:
                msgout = {'fail':1}
            else:
                if not stderr:
                    msgout = {'filename':fileobj.filename,'text':stdout.strip().decode('utf-8'),'database':msg['database'],'collection':msg['collection']}
        except OSError as e :
#            print e
            msgout = {'fail':1}
            try:
                p1.kill()
                p2.kill()
            except OSError:
                pass #process is already dead

        return msgout

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
