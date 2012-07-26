from django.shortcuts import render_to_response, get_object_or_404,redirect
from django.core.context_processors import csrf
from django.http import Http404,HttpResponse, HttpResponseRedirect
from django.core import serializers
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import simplejson
import zipfile
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, DetailView
#from taw.models import *
from taw.forms import CorpusForm, DocumentForm
from django.conf import settings
import pymongo as PM
from bson import ObjectId
import sphinxapi
import json
import os
import datetime
import mimetypes
from pypln.stores.mongo import MongoDBStore





# Initialize mongo connection
MS = MongoDBStore(**{'host':'127.0.0.1','port':27017,
                   'database': 'pypln',
                    'corpora_collection': 'corpora',
                    'document_collection': 'documents',
                    'analysis_collection': 'analysis',
                    'gridfs_collection': 'files',
                    'monitoring_collection': 'monitoring'})
Corpus = MS.Corpus
Document = MS.Document

#TODO: the configuration from the Mongodb Store should be pulled from some global config file.
connection = PM.Connection(settings.MONGODB, settings.MONGODB_PORT)




def main(request):
    return render_to_response("taw/workbench.html", context_instance=RequestContext(request))


@login_required
def corpora_page(request):
    """
    View of list of corpora available
    :param request:
    :return:
    """
    form = CorpusForm()
    if request.method == 'POST':
        form = CorpusForm(request.POST)
        if form.is_valid():
            create_corpus(request.POST,request.user)
            return HttpResponseRedirect('/taw/corpora/') # Redirect after POST
    corpora = list(MS.Corpus.all)
    data_dict = {
        'corpora': corpora,
        'form': form,
    }

    return render_to_response('taw/corpora.html',data_dict, context_instance=RequestContext(request))

@login_required
def corpora_as_JSON(request):
    """
    Returns list of corpora in JSON format
    :param request:
    :return:
    """
    data = json.dumps([{'name':c.name,'slug':c.slug} for c in Corpus.all])
    return HttpResponse(data,mimetype='application/json')

@login_required
def add_docs_to_corpus(request):
    """
    From a post request, add a list of documents identified by their IDs to
    a corpus. This view is for documents which are already stored in the system.
    :param request:
    :return:
    """
    if request.method == 'POST':
        print request.POST.items()
        doc_ids = [v for k,v in request.POST.items() if k.startswith('option')]
        corpus = request.POST['corpus']
        for did in doc_ids:
            d = Document.find_by_id(did)
            d.corpora.append(corpus)
            d.save()
    return HttpResponseRedirect('/taw/') # Redirect after POST



def create_corpus(data, usr):
    """
    Create corpus in the database.
    :param data: dictionary with corpus info from post request
    :param usr: User creating the corpus
    :return: None
    """
    c = Corpus(**{"name"      :data['name'],
                'description' :data['description'],
                'owner'       : usr.id,
                'private'     : data['private'],
                })
    c.save()


@login_required
def corpus(request,corpus_slug=""):
    """
    Render a single corpus view, when receiving a GET or Add uploaded documents to corpus when
    receiving a POST
    :param request:
    :param corpus_slug: name (slug) of the corpus in the corpora collection
    :return:
    """
    form = DocumentForm()
    docs = [] #this should be fetched from corpus if it exists
    if request.method == 'POST':
        form = DocumentForm(request.POST,request.FILES)
        save_uploaded_documents(request.FILES['file'], corpus_slug, request.user.id)
        return HttpResponseRedirect("/taw/corpus/"+corpus_slug+"/")
    #TODO: integrate with DocumentStore

    c = Corpus.find_by_slug(corpus_slug)
    docs.append(Document.find_by_corpora(corpus_slug))
    #TODO: fetch metadata for docs: _id(to be able to show and manipulate),size, owner, date uploaded, etc.
    data_dict = {
        "owner"        : c.owner,
        "slug"          : c.slug,
        "name"          : c.name,
        "date_created"  : c.date_created,
        "document_list" : docs,
        "form"          : form,
    }
    return render_to_response("taw/corpus.html", data_dict, context_instance=RequestContext(request))

def save_uploaded_documents(fobj, corpus_slug, uid):
    """
    Save uploaded documents in the document store
    :param fobj: fileobject uploaded
    :return: list of documents
    """
    fname  = fobj.name
    if mimetypes.guess_type(fname)[0] == 'application/zip':
        process_zip_file(fobj,corpus_slug, uid)
    else:
        doc = Document(filename=fname)
        doc.corpora.append(corpus_slug)
        doc.owner = uid
        doc.save()
        doc.set_blob(fobj.read())

    #TODO: check if file is an archive and extract the individual files from it before adding them to gridfs
    return []

def process_zip_file(f, corpus_slug, uid):
    """
    Extracts files of a zip archive and return them as a list of file objects
    :param f: File object of a zip archive
    :return: list of file objects contained in the zip file
    """
    zip = zipfile.ZipFile(f)
    bad_file = zip.testzip()
    if bad_file:
        raise Exception('"%s" in the .zip archive is corrupt.' %f.name)
    for filename in sorted(zip.namelist()):
        data = zip.read(filename)
        doc = Document(filename=filename, owner=uid)
        doc.save()
        doc.set_blob(data)
    zip.close()

def search(request):
    """
    Perform a fulltext search on all collections.
    :param request:
    :param query: Query string
    :return:
    """
    query = request.GET.get('query', None)
    if query is None:
        return HttpResponse('', mimetype="application/json")
    elif query == '':
        return HttpResponse('', mimetype="application/json")

    cl = sphinxapi.SphinxClient()
    cl.SetServer(settings.SPHINXSEARCH_HOST, settings.SPHINXSEARCH_PORT)
    cl.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED)
    #cl.SetGroupBy('collection',sphinxapi.SPH_GROUPBY_ATTR)
    res = cl.Query(query)
    results = []
    fields = {'text': 1, 'filename': 1, 'size': 1, 'text': 1}
    for match in res["matches"]:
        _id = match["attrs"]["_id"]
        result = connection[match['attrs']['db']][match['attrs']['collection']].find({'_id': ObjectId(_id)}, fields)
        if result.count():
            document = result[0]
            results.append({'_id': _id, 'filename': document['filename'], 'text': document['text'],
                            'db': match['attrs']['db'], 'collection': match['attrs']['collection']})
    excerpts = cl.BuildExcerpts([document['text'] for document in results], 'artigos', query)
    keywords = cl.BuildKeywords(query.encode('utf8'),'artigos',1)
    for index, document in enumerate(results):
        document['excerpt'] = excerpts[index]
        del document['text']

    stats = {"total_found"  : res['total_found'],
             "time"         : res['time'],
             "words"        : res['words']
             }
    return HttpResponse(json.dumps({'results':results,'stats':stats}), mimetype="application/json")

def document_view(request, document_id):
    """
    This view assembles the document analysis page
    :param request:
    :param document_id:
    :return:
    """
    doc = Document.find_by_id(document_id)
    id, db, collection = document_id.strip('/').split('|')
    fields = {'text': 1, 'filename': 1, 'size': 1}
    result = connection[db][collection].find({"_id":ObjectId(id)},fields)
    if result.count():
            text = result[0]['text']
            fname = result[0]['filename']
            size  = result[0].get('size','N/A')

    else:
        text = "Document not Found"
        fname = ""
        size = 0
    data_dict = {
        "doc_id"    : document_id,
        "filename"  : fname,
        "text"      : text,
        "size"      : size,
    }
    return render_to_response("taw/document.html", data_dict, context_instance=RequestContext(request))
