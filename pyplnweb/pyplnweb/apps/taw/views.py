from django.shortcuts import render_to_response, get_object_or_404,redirect
from django.core.context_processors import csrf
from django.http import Http404,HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, DetailView
from taw.models import *
from taw.forms import CorpusForm, DocumentForm
from django.conf import settings
import pymongo as PM
from bson import ObjectId
import sphinxapi
import json
import os
import datetime
#from pypln.stores import DocumentStore
#DS = DocumentStore()

# Initialize mongo connection
connection = PM.Connection(settings.MONGODB, settings.MONGODB_PORT)


def main(request):
    return render_to_response("taw/workbench.html", context_instance=RequestContext(request))



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
    corpora = connection.pypln.corpora.find()
    data_dict = {
        'corpora': list(corpora),
        'form': form
    }

    return render_to_response('taw/corpora.html',data_dict, context_instance=RequestContext(request))


def create_corpus(data, owner):
    """
    Create corpus in the database.
    :param data: dictionary with corpus info from post request
    :return: None
    """
    connection.pypln.corpora.insert({"name"         :data['name'],
                                     'description'  :data['description'],
                                     'owner'        : owner,
                                     'created_on'   : datetime.datetime.now(),
                                     'last_updated' : datetime.datetime.now(),
                                     'docs'         : [],
                                     'private'       : data['private'],
                                    })

def collection_browse(request):
    """
    This view assembles the collection browsw page
    """
    dbs = connection.database_names()
    collections = {}
    for db in dbs:
        d = connection[db]
        for col in d.collection_names():
            collections[col] = {'db':db, 'count':d[col].count()}

    data_dict = {'collections':collections,

    }
    data_dict.update(csrf(request))
    return render_to_response("taw/collections.html", data_dict, context_instance=RequestContext(request))

def document_browse(request, dbname,collname):
    """
    List of documents for a given collection.
    Also
    """
    docs = connection[dbname][collname].find(limit=100)
    keys = docs[0].keys()
    if request.user.is_authenticated():
        corpora = Corpus.objects.filter(owner=request.user)
    else:
        corpora = []
    cform = CorpusForm()
    data_dict = {'docs':docs,
                 'keys':keys,
                 'jkeys':simplejson.dumps(keys),
                 'db':simplejson.dumps(dbname),
                 'collection':simplejson.dumps(collname),
                 'corpora':corpora,
                 'corpusform':cform,
    }
    data_dict.update(csrf(request))
    return render_to_response("taw/document_browse.html", data_dict, context_instance=RequestContext(request))



@login_required
def corpus(request,corpus_slug=""):
    """
    Render a single corpus view
    :param request:
    :param corpus_slug: name (slug) of the corpus in the corpora collection
    :return:
    """
    form = DocumentForm()
    docs = [] #this should be fetched from corpus if it exists
    if request.method == 'POST':
        form = DocumentForm(request.POST,request.FILES)
        docs = save_uploaded_documents(request.FILES['file'])
        return HttpResponseRedirect("/taw/corpus/"+corpus_slug+"/")
    #TODO: integrate with DocumentStore
    data_dict = {
        "slug"          : corpus_slug,
        "name"          : corpus_slug,
        "document_list" : docs,
        "form"          : form,
    }
    return render_to_response("taw/corpus.html", data_dict, context_instance=RequestContext(request))

def save_uploaded_documents(fobj):
    """
    Save uploaded documents in the document store
    :param fobj: fileobject uploaded
    :return: list of documents
    """
    fname  = fobj.name
    gfs = open(os.path.join('/tmp/',fname),'w')
    for chunk in fobj.chunks():
        gfs.write(chunk)
    #TODO: check if file is an archive and extract the individual files from it before adding them to gridfs
    return []

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
