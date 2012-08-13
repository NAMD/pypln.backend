# coding: utf-8

import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from pypln.models import Corpus, Document, CorpusForm, DocumentForm


def index(request):
    return render_to_response('pypln/homepage.html', {},
            context_instance=RequestContext(request))

@login_required
def corpora_list(request):
    if request.method == 'POST':
        form = CorpusForm(request.POST)
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
    return render_to_response('pypln/corpora.html', data,
            context_instance=RequestContext(request))

@login_required
def corpus_page(request, corpus_slug):
    try:
        corpus = Corpus.objects.get(slug=corpus_slug, owner=request.user.id)
    except ObjectDoesNotExist:
        return render_to_response('pypln/404.html', {},
                context_instance=RequestContext(request))
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if not form.is_valid():
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
            request.user.message_set.create(message=_('Document uploaded '
                                                      'successfully!'))
            return HttpResponseRedirect(reverse('corpus_page',
                    kwargs={'corpus_slug': corpus_slug}))
    else:
        form = DocumentForm()
    form.fields['blob'].label = ''
    data = {'corpus': corpus, 'form': form}
    return render_to_response('pypln/corpus.html', data,
            context_instance=RequestContext(request))

@login_required
def document_page(request, document_slug):
    try:
        document = Document.objects.get(slug=document_slug, owner=request.user.id)
    except ObjectDoesNotExist:
        return render_to_response('pypln/404.html', {},
                context_instance=RequestContext(request))

    data = {'document': document,
            'corpora': Corpus.objects.filter(owner=request.user.id)}
    return render_to_response('pypln/document.html', data,
        context_instance=RequestContext(request))

@login_required
def document_list(request):
    data = {'documents': Document.objects.filter(owner=request.user.id)}
    return render_to_response('pypln/documents.html', data,
            context_instance=RequestContext(request))

@login_required
def document_download(request, document_slug):
    return HttpResponse('#TODO')
