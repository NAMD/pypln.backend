# coding: utf-8

from nltk import pos_tag


__meta__ = {'work on': 'document',
            'requires': ['text', 'tokens'],
            'provides': ['pos'],}
#TODO: add 'lang' to 'requires'

def put_offset(text, tagged_text):
    result = []
    position = 0
    for token, classification in tagged_text:
        token_position = text.find(token, position)
        result.append((token, classification, token_position))
        position = token_position + len(token) - 1
    return result

def main(document):
    text = document['text']
    tokens = document['tokens']
    tagged_text = pos_tag(tokens)
    return {'pos': put_offset(text, tagged_text)}
