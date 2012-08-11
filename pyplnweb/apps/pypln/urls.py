from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('pypln.views',
        url(r'^corpora/?$', 'corpora_list', name='corpora_list'),
        url(r'^corpora/(?P<corpus_slug>.+)/?$', 'corpus_page',
            name='corpus_page'),
        url(r'^document/(?P<document_slug>.+)/?$', 'document_page',
            name='document_page'),
)
