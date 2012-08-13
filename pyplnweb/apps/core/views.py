# coding: utf-8

import datetime
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
from pyplnweb.settings import MANAGER_API_HOST_PORT, MANAGER_TIMEOUT
from pypln.client import ManagerClient


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
            filename = new_document.file_name()
            filename = ' '.join(filename.split('.')[:-1])
            new_document.slug = slugify(filename)
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
    return render_to_response('core/document.html', data,
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
