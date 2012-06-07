# coding: utf-8

__meta__ = {'from': 'gridfs-file',
            'requires': ['contents', 'meta'],
            'to': 'document',
            'provides': ['text', 'metadata'],}

import shlex
from subprocess import Popen, PIPE
from mimetypes import guess_type
from re import compile as re_compile


regexp_tags = re_compile(r'(<[ \t]*(/?[a-zA-Z]*)[^>]*>)')

def parse_html(html, remove_tags=None, remove_inside=None, replace_with=' '):
    data = regexp_tags.split(html)
    content_between = data[::3]
    complete_tags = data[1::3]
    tag_names = data[2::3]
    to_remove = []
    for index, tag_name in enumerate(tag_names):
        search_tag = tag_name
        if tag_name and tag_name[0] == '/':
            search_tag = tag_name[1:]
        if remove_tags and search_tag not in remove_inside:
            complete_tags[index] = replace_with
        if remove_inside and tag_name in remove_inside:
            remove_to = tag_names.index('/' + tag_name, index)
            total_to_remove = remove_to - index + 1
            complete_tags[index:remove_to + 1] = [''] * total_to_remove
            content_between[index + 2:remove_to + 1] = [''] * (total_to_remove - 2)
            content_between[index + 1] = '\n'
    complete_tags.append('')
    return ''.join(sum(zip(content_between, complete_tags), tuple()))

def get_pdf_metadata(data):
    lines = data.strip().splitlines()
    metadata = {}
    for line in lines:
        try:
            key, value = line[:line.index(':')], line[line.index(':') + 1:]
        except ValueError:
            continue
        metadata[key.strip()] = value.strip()
    return metadata

def extract_pdf(data):
    pdf2text = Popen(shlex.split('pdftotext -q - -'), stdin=PIPE, stdout=PIPE,
                     stderr=PIPE)
    pdfinfo = Popen(shlex.split('pdfinfo -meta -'), stdin=PIPE, stdout=PIPE,
                    stderr=PIPE)
    text, text_err = pdf2text.communicate(input=data)
    meta_out, meta_err = pdfinfo.communicate(input=data)
    try:
        metadata = get_pdf_metadata(meta_out)
    except:
        pass
        #TODO: what should I do here?
    if not (text and metadata):
        return None, None
    elif not text_err:
        return text.strip(), None if meta_err else metadata
    else:
        return None, None

def main(file_data):
    file_mime_type = guess_type(file_data['name'])[0]
    metadata = None
    if file_mime_type == 'text/plain':
        text = file_data['contents']
    elif file_mime_type == 'text/html':
        text = parse_html(file_data['contents'], True, ['script', 'style'])
    elif file_mime_type == 'application/pdf':
        text, metadata = extract_pdf(file_data['contents'])
    return {'text': text, 'metadata': metadata}

#TODO: detect language with cld
#TODO: detect encoding to decode
#TODO: should extractor add file-metadata (creation date, size etc.)?
#TODO: need to verify some exceptions when trying to convert 'evil' PDFs
#TODO: should 'replace_with' be '' when extracting from HTML?
