#-*- coding:utf-8 -*-
"""
This worker does Part of speech tagging.

Created on 28/09/11
by flavio
"""
__author__ = 'flavio'
__docformat__ = "restructuredtext en"

import zmq
from base import PushPullWorker
from nltk import pos_tag, word_tokenize
from nltk.data import LazyLoader
from nltk.tag import tuple2str
from zmq import ZMQError


context = zmq.Context()
eng_sent_tokenizer = LazyLoader('tokenizers/punkt/english.pickle')
port_sent_tokenizer = LazyLoader('tokenizers/punkt/portuguese.pickle')
#TODO: alow the usage of PaLavras when tagging portuguese texts

class POSTaggerWorker(PushPullWorker):
    """
    Worker to tag words in texts according to their morphological type
    Expects to receive a JSON message with the following structure
    {"text":"...","lang":"<language iso code>"} where text is a raw text string.
    To be used together with the MongoUpdateSink class.
    """

    def process(self,msg):
        """Does the POS tagging"""
        try:
            if msg['lang'] == 'en':
                sents = eng_sent_tokenizer.tokenize(msg['text'])
            elif msg['lang'] == 'pt':
                sents = port_sent_tokenizer.tokenize(msg['text'])
            tokens = []
            for s in sents:
                tokens.extend(pos_tag(word_tokenize(s)))
            tagged_text = ' '.join([tuple2str(t) for t in tokens])
            msgout = {"database": msg['database'],
                      "collection": msg['collection'],
                      "spec": {"_id": msg['_id']},
                      "update": {"$set": {'tagged_text': tagged_text}},
                      "multi":False}
            self.sender.send_json(msgout)
        except ZMQError:
            self.sender.send_json({'fail': 1})
