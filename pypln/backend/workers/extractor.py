# coding: utf-8
#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN. You can get more information at: http://pypln.org/.
#
# PyPLN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPLN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPLN.  If not, see <http://www.gnu.org/licenses/>.

import shlex

from tempfile import NamedTemporaryFile
from os import unlink
from subprocess import Popen, PIPE
from mimetypes import guess_type
from re import compile as regexp_compile, DOTALL, escape

import cld

from pypelinin import Worker


regexp_tags = regexp_compile(r'(<[ \t]*([a-zA-Z0-9!"./_-]*)[^>]*>)', flags=DOTALL)
regexp_comment = regexp_compile(r'<!--.*?-->', flags=DOTALL)
regexp_spaces_start = regexp_compile('([\n]+)[ \t]*',
        flags=DOTALL)
regexp_spaces_end = regexp_compile('[ \t]*\n', flags=DOTALL)
regexp_newlines = regexp_compile('[\n]{3,}', flags=DOTALL)
regexp_spaces = regexp_compile('[ \t]{2,}', flags=DOTALL)
regexp_punctuation = regexp_compile('[ \t]*([' + escape('!,.:;?') + '])',
        flags=DOTALL)
breakline_tags = ['table', '/table', 'tr', 'div', '/div', 'h1', '/h1', 'h2',
                  '/h2', 'h3', '/h3', 'h4', '/h4', 'h5', '/h5', 'h6', '/h6',
                  'br', 'br/']
double_breakline = ['table', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']

def clean(text):
    text = regexp_spaces_start.sub(r'\1', text)
    text = regexp_spaces_end.sub('\n', text)
    text = regexp_newlines.sub('\n\n', text)
    text = regexp_spaces.sub(' ', text)
    text = regexp_punctuation.sub(r'\1', text)
    return text.strip()

def parse_html(html, remove_tags=None, remove_inside=None,
               replace_space_with=' ', replace_newline_with='\n'):
    html = regexp_comment.sub('', html.replace('\n', ''))
    data = regexp_tags.split(html)
    content_between = data[::3]
    complete_tags = data[1::3]
    tag_names = [x.lower() for x in data[2::3]]
    for index, tag_name in enumerate(tag_names):
        if not tag_name.strip():
            continue
        search_tag = tag_name
        if tag_name and tag_name[0] == '/':
            search_tag = tag_name[1:]
        if remove_tags and search_tag not in remove_inside:
            if tag_name in breakline_tags:
                if search_tag in double_breakline:
                    complete_tags[index] = 2 * replace_newline_with
                else:
                    complete_tags[index] = replace_newline_with
            else:
                complete_tags[index] = replace_space_with
        if remove_inside and tag_name in remove_inside:
            remove_to = tag_names.index('/' + tag_name, index)
            total_to_remove = remove_to - index + 1
            complete_tags[index:remove_to + 1] = [''] * total_to_remove
            content_between[index + 2:remove_to + 1] = \
                    [''] * (total_to_remove - 2)
            content_between[index + 1] = '\n'
    complete_tags.append('')
    result = ''.join(sum(zip(content_between, complete_tags), tuple()))
    return clean(result)

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
    temp = NamedTemporaryFile(delete=False)
    filename = temp.name
    temp.close()
    pdf2html = Popen(shlex.split('pdftohtml -q -i - {}'.format(temp.name)),
                     stdin=PIPE, stdout=PIPE, stderr=PIPE)
    html, html_err = pdf2html.communicate(input=data)
    fp = open(filename + 's.html', 'r')
    html = fp.read()
    fp.close()
    unlink(filename + '.html')
    unlink(filename + '_ind.html')
    unlink(filename + 's.html')
    text = parse_html(html.replace('&#160;', ' '), True, ['script', 'style'])
    pdfinfo = Popen(shlex.split('pdfinfo -'), stdin=PIPE, stdout=PIPE,
                    stderr=PIPE)
    meta_out, meta_err = pdfinfo.communicate(input=data)
    try:
        metadata = get_pdf_metadata(meta_out)
    except:
        metadata = {}
        #TODO: what should I do here?
    if not (text and metadata):
        return '', {}
    elif not html_err:
        return text, {} if meta_err else metadata
    else:
        return '', {}


class Extractor(Worker):
    #TODO: detect encoding to decode
    #TODO: need to verify some exceptions when trying to convert 'evil' PDFs
    #TODO: should 'replace_with' be '' when extracting from HTML?
    requires = ['contents']

    def process(self, file_data):
        file_mime_type = guess_type(file_data['filename'])[0]
        metadata = {}
        if file_mime_type == 'text/plain':
            text = file_data['contents']
        elif file_mime_type == 'text/html':
            text = parse_html(file_data['contents'], True, ['script', 'style'])
        elif file_mime_type == 'application/pdf':
            text, metadata = extract_pdf(file_data['contents'])
        text = clean(text)
        language = cld.detect(text)[1]
        return {'text': text, 'file_metadata': metadata, 'language': language}
