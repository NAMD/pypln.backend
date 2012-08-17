# coding: utf-8

import datetime
import json
from mimetypes import guess_type
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from .models import Corpus, Document, CorpusForm, DocumentForm
from core.util import LANGUAGES
from pyplnweb.settings import (MANAGER_API_HOST_PORT, MANAGER_TIMEOUT,
                               MONGODB_CONFIG)
from pypln.client import ManagerClient
from mongodict import MongoDict


def _token_frequency_histogram(data):
    from collections import Counter

    freqdist = data['freqdist']
    values = Counter()
    for key, value in freqdist:
        values[value] += 1
    data['values'] = [list(x) for x in values.most_common()]
    del data['freqdist']
    return data


VISUALIZATIONS = {
        'text': {
            'label': _('Plain text'),
            'requires': set(['text']),
        },
        'pos-highlighter': {
            'label': _('Part-of-speech'),
            'requires': set(['pos', 'tokens'])
        },
        'token-frequency-histogram': {
             'label': _('Token frequency histogram'),
             'requires': set(['freqdist', 'momentum_1', 'momentum_2',
                              'momentum_3', 'momentum_4']),
             'process': _token_frequency_histogram,
        },
        'statistics': {
            'label': _('Statistics'),
            'requires': set(['tokens', 'sentences', 'repertoire',
                             'average_sentence_repertoire',
                             'average_sentence_length'])
        },
}

def _slug(filename):
    return '.'.join([slugify(x) for x in filename.split('.')])

def _create_pipeline(api_host_port, data, timeout=1):
    client = ManagerClient()
    client.connect(api_host_port=api_host_port)
    client.send_api_request({'command': 'add pipeline', 'data': data})
    if client.api_poll(timeout):
        return client.get_api_reply()
    else:
        return False

def index(request):
    return render_to_response('core/homepage.html', {},
            context_instance=RequestContext(request))

@login_required
def corpora_list(request):
    if request.method == 'POST':
        form = CorpusForm(request.POST)
        #TODO: do not permit to insert duplicated corpus
        if not form.is_valid():
            request.user.message_set.create(message=_('ERROR: all fields are '
                                                      'required!'))
        else:
            new_corpus = form.save(commit=False)
            new_corpus.slug = slugify(new_corpus.name)
            new_corpus.owner = request.user
            new_corpus.date_created = datetime.datetime.now()
            new_corpus.last_modified = datetime.datetime.now()
            new_corpus.save()
            request.user.message_set.create(message=_('Corpus created '
                                                      'successfully!'))
            return HttpResponseRedirect(reverse('corpora_list'))
    else:
        form = CorpusForm()

    data = {'corpora': Corpus.objects.filter(owner=request.user.id),
            'form': form}
    return render_to_response('core/corpora.html', data,
            context_instance=RequestContext(request))

@login_required
def corpus_page(request, corpus_slug):
    try:
        corpus = Corpus.objects.get(slug=corpus_slug, owner=request.user.id)
    except ObjectDoesNotExist:
        return render_to_response('core/404.html', {},
                context_instance=RequestContext(request))
    if request.method == 'POST':
        #TODO: accept (and uncompress) .tar.gz and .zip files
        #TODO: enforce document type
        #TODO: dot not permit to have documents with the same slug!
        form = DocumentForm(request.POST, request.FILES)
        if not form.is_valid():
            #TODO: put messages to work
            request.user.message_set.create(message=_('ERROR: you need to '
                                                      'select a file!'))
        else:
            new_document = form.save(commit=False)
            new_document.slug = ''
            new_document.owner = request.user
            new_document.date_uploaded = datetime.datetime.now()
            new_document.save()
            new_document.slug = _slug(new_document.file_name())
            new_document.corpus_set.add(corpus)
            for corpus in new_document.corpus_set.all():
                corpus.last_modified = datetime.datetime.now()
                corpus.save()
            new_document.save()
            data = {'_id': str(new_document.blob.file._id),
                    'id': new_document.id}
            _create_pipeline(MANAGER_API_HOST_PORT, data,
                             timeout=MANAGER_TIMEOUT)
            request.user.message_set.create(message=_('Document uploaded '
                                                      'successfully!'))
            return HttpResponseRedirect(reverse('corpus_page',
                    kwargs={'corpus_slug': corpus_slug}))
    else:
        form = DocumentForm()
    form.fields['blob'].label = ''
    data = {'corpus': corpus, 'form': form}
    return render_to_response('core/corpus.html', data,
            context_instance=RequestContext(request))

@login_required
def document_page(request, document_slug):
    try:
        document = Document.objects.get(slug=document_slug,
                owner=request.user.id)
    except ObjectDoesNotExist:
        return render_to_response('core/404.html', {},
                context_instance=RequestContext(request))

    data = {'document': document,
            'corpora': Corpus.objects.filter(owner=request.user.id)}
    store = MongoDict(host=MONGODB_CONFIG['host'], port=MONGODB_CONFIG['port'],
                      database=MONGODB_CONFIG['database'],
                      collection=MONGODB_CONFIG['analysis_collection'])
    analysis = set(store.get('id:{}:analysis'.format(document.id), []))
    metadata = store.get('id:{}:file-metadata'.format(document.id), {})
    language = store.get('id:{}:language'.format(document.id), None)
    if language is not None:
        metadata['language'] = LANGUAGES[language]
    data['metadata'] = metadata
    visualizations = []
    for key, value in VISUALIZATIONS.items():
        if value['requires'].issubset(analysis):
            visualizations.append({'slug': key, 'label': value['label']})
    data['visualizations'] = visualizations
    return render_to_response('core/document.html', data,
        context_instance=RequestContext(request))

@login_required
def document_visualization(request, document_slug, visualization):
    try:
        document = Document.objects.get(slug=document_slug,
                owner=request.user.id)
    except ObjectDoesNotExist:
        return HttpResponse('Document not found', status_code=404)

    data = {}
    store = MongoDict(host=MONGODB_CONFIG['host'], port=MONGODB_CONFIG['port'],
                      database=MONGODB_CONFIG['database'],
                      collection=MONGODB_CONFIG['analysis_collection'])

    try:
        analysis = set(store['id:{}:analysis'.format(document.id)])
    except KeyError:
        return HttpResponse('Visualization not found', status_code=404)
    if visualization not in VISUALIZATIONS or \
            not VISUALIZATIONS[visualization]['requires'].issubset(analysis):
        return HttpResponse('Visualization not found', status_code=404)

    data = {}
    for key in VISUALIZATIONS[visualization]['requires']:
        data[key] = store['id:{}:{}'.format(document.id, key)]
    view_name = 'core/visualizations/{}.html'.format(visualization)
    if 'process' in VISUALIZATIONS[visualization]:
        data = VISUALIZATIONS[visualization]['process'](data)
    return render_to_response(view_name, data,
            context_instance=RequestContext(request))

@login_required
def document_list(request):
    data = {'documents': Document.objects.filter(owner=request.user.id)}
    return render_to_response('core/documents.html', data,
            context_instance=RequestContext(request))

@login_required
def document_download(request, document_slug):
    try:
        document = Document.objects.get(slug=document_slug,
                owner=request.user.id)
    except ObjectDoesNotExist:
        return render_to_response('core/404.html', {},
                context_instance=RequestContext(request))
    filename = document.blob.name.split('/')[-1]
    file_mime_type = guess_type(filename)[0]
    response = HttpResponse(document.blob, content_type=file_mime_type)
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
    return response
