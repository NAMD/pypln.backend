# coding: utf-8

from pypelinin import Worker

from nltk import pos_tag


def _put_offset(text, tagged_text):
    result = []
    position = 0
    for token, classification in tagged_text:
        token_position = text.find(token, position)
        result.append((token, classification, token_position))
        position = token_position + len(token) - 1
    return result

class POS(Worker):
    requires = ['text', 'tokens', 'language']

    def process(self, document):
        tagged_text = None
        if document['language'] == 'en':
            tagged_text = _put_offset(document['text'],
                                      pos_tag(document['tokens']))
        return {'pos': tagged_text}
