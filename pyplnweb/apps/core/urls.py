from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('core.views',
        url(r'^corpora/?$', 'corpora_list', name='corpora_list'),
        url(r'^corpora/(?P<corpus_slug>.+)/?$', 'corpus_page',
            name='corpus_page'),
        url(r'^documents/?$', 'document_list', name='document_list'),
        url(r'^document/(?P<document_slug>.+)/download$', 'document_download',
            name='document_download'),
        url(r'^document/(?P<document_slug>.+)/?$', 'document_page',
            name='document_page'),
)
