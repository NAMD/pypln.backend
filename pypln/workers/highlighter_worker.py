#-*- coding:utf-8 -*-
"""
This worker highlights words on a document using html and CSS.

Created on 26/02/12

"""
__author__ = 'fccoelho'


import zmq
from base import PushPullWorker

class HighlighterWorker(PushPullWorker):
    """
    This worker takes a tokenized text and a dictionary with keys and lists of words to be highlighted.
    Returning same tags with words highlighted according to pertinence to each list of words
    msg format:
    {'text':['the','cat',...],'wordlists':{}}
    """

    def process(self,msg):
        """
        Does the highlighting
        """
        new_text = []
        for i,word in enumerate(msg['text']):
            belongs = []
            for k,wl in msg['wordlists'].items():
                if word in wl:
                    word_tagged = '<span class="tagged" title="%s"><b>'+word+'</b></span>'
                    # print k
                    belongs.append(k)
                # print "==>",k, belongs, word
            if belongs:
                new_text.append(word_tagged%(','.join(belongs)))
            else:
                new_text.append(word)
        msgout = {'highlighted_text':new_text}
        try:
            self.sender.send_json(msgout)
        except AttributeError:
            #this is necessary so that we can test this method without starting the worker as a daemon
            pass
        return msgout #for testing purposes
