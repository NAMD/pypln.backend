# coding: utf-8

from unicodedata import normalize


def slug(text, encoding='utf-8',
         permitted_chars='abcdefghijklmnopqrstuvwxyz0123456789-'):
    '''Create a slug from a text, with configurable permitted characters

    Learn more at:
    `Slug on Wikipedia <https://en.wikipedia.org/wiki/Slug_(web_publishing)>`_
    '''
    if isinstance(text, str):
        text = text.decode(encoding or 'ascii')
    clean_text = text.strip().replace(' ', '-').lower()
    while '--' in clean_text:
        clean_text = clean_text.replace('--', '-')
    ascii_text = normalize('NFKD', clean_text).encode('ascii', 'ignore')
    strict_text = map(lambda x: x if x in permitted_chars else '', ascii_text)
    return ''.join(strict_text)
