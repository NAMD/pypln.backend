# coding: utf-8

import unittest
import datetime
import pymongo
from gridfs import GridFS
from pypln.stores.mongo import MongoDBStore, slug
from bson import ObjectId


class TestSlug(unittest.TestCase):
    def test_should_always_return_lowercase_words(self):
        self.assertEquals(slug('ALVAROJUSTEN'), 'alvarojusten')

    def test_should_replace_space_with_dash(self):
        self.assertEquals(slug('Alvaro Justen'), 'alvaro-justen')

    def test_should_ignore_unecessary_spaces(self):
        self.assertEquals(slug('  alvaro   justen  '), 'alvaro-justen')

    def test_should_replace_nonascii_chars_with_corresponding_ascii_chars(self):
        self.assertEquals(slug('áÁàÀãÃâÂäÄ'.decode('utf8')), 'aaaaaaaaaa')
        self.assertEquals(slug('éÉèÈẽẼêÊëË'.decode('utf8')), 'eeeeeeeeee')
        self.assertEquals(slug('íÍìÌĩĨîÎïÏ'.decode('utf8')), 'iiiiiiiiii')
        self.assertEquals(slug('óÓòÒõÕôÔöÖ'.decode('utf8')), 'oooooooooo')
        self.assertEquals(slug('úÚùÙũŨûÛüÜ'.decode('utf8')), 'uuuuuuuuuu')
        self.assertEquals(slug('ćĆĉĈçÇ'.decode('utf8')), 'cccccc')

    def test_should_accept_unicode_text(self):
        self.assertEquals(slug(u'Álvaro Justen'), 'alvaro-justen')

    def test_should_accept_other_input_encodings(self):
        slugged_text = slug(u'Álvaro Justen'.encode('utf16'), 'utf16')
        self.assertEquals(slugged_text, 'alvaro-justen')

    def test_should_accept_only_ascii_letters_and_numbers(self):
        slugged_text = slug('''qwerty123456"'@#$%*()_+\|<>,.;:/?]~[`{}^ ''')
        self.assertEquals(slugged_text, 'qwerty123456')

    def test_should_accept_only_chars_in_permitted_chars_parameter(self):
        slugged_text = slug('''0987654321gfdsazxcvb''',
                            permitted_chars='abc123')
        self.assertEquals(slugged_text, '321acb')

class TestMongoStore(unittest.TestCase):
    def setUp(self):
        config = {'db': {'host': 'localhost', 'port': 27017,
                         'database': 'pypln',
                         'corpora_collection': 'corpora',
                         'document_collection': 'documents',
                         'gridfs_collection': 'files',
                         'monitoring_collection': 'monitoring'},
                  'monitoring interval': 60,}
        #TODO: unify config
        self.db_conf = db_conf = config['db']
        self.connection = pymongo.Connection(host=db_conf['host'],
                                             port=db_conf['port'])
        self.db = self.connection[db_conf['database']]
        self.documents = self.db[db_conf['document_collection']]
        self.gridfs = GridFS(self.db, db_conf['gridfs_collection'])
        self.corpora = self.db[self.db_conf['corpora_collection']]
        self.store = MongoDBStore(**db_conf)
        self.documents.drop()
        self.corpora.drop()
        self.db[db_conf['gridfs_collection'] + '.files'].drop()
        self.db[db_conf['gridfs_collection'] + '.chuncks'].drop()

    def tearDown(self):
        self.connection.drop_database(self.db)

    def test_add_corpus(self):
        new_corpus = self.store.Corpus()
        new_corpus.name = 'Just Testing'
        new_corpus.owner = u'Álvaro Justen'
        new_corpus.description = u'This is just a test'
        new_corpus.save()
        corpus_id = new_corpus._id
        cursor = self.corpora.find()
        self.assertEquals(cursor.count(), 1)
        corpus = cursor[0]
        self.assertEquals(corpus['_id'], corpus_id)
        self.assertEquals(corpus['name'], 'Just Testing')
        self.assertEquals(corpus['slug'], 'just-testing')
        self.assertEquals(corpus['description'], u'This is just a test')
        self.assertEquals(corpus['owner'], u'Álvaro Justen')
        self.assertEquals(type(corpus['date_created']), datetime.datetime)
        self.assertEquals(type(corpus['last_modified']), datetime.datetime)
        self.assertEquals(corpus['last_modified'], corpus['date_created'])
        self.assertEquals(corpus['_id'], new_corpus._id)
        self.assertEquals(corpus['name'], new_corpus.name)
        self.assertEquals(corpus['slug'], new_corpus.slug)
        self.assertEquals(corpus['description'], new_corpus.description)
        self.assertEquals(corpus['owner'], new_corpus.owner)
        self.assertEquals(corpus['date_created'], new_corpus.date_created)
        self.assertEquals(corpus['last_modified'], new_corpus.last_modified)

    def test_add_corpus_using_keywords(self):
        new_corpus = self.store.Corpus(name='Just Testing',
                                       owner=u'Álvaro Justen',
                                       description=u'This is just a test')
        new_corpus.save()
        corpus_id = new_corpus._id
        cursor = self.corpora.find()
        self.assertEquals(cursor.count(), 1)
        corpus = cursor[0]
        self.assertEquals(corpus['_id'], corpus_id)
        self.assertEquals(corpus['name'], 'Just Testing')
        self.assertEquals(corpus['slug'], 'just-testing')
        self.assertEquals(corpus['description'], u'This is just a test')
        self.assertEquals(corpus['owner'], u'Álvaro Justen')
        self.assertEquals(type(corpus['date_created']), datetime.datetime)
        self.assertEquals(type(corpus['last_modified']), datetime.datetime)
        self.assertEquals(corpus['last_modified'], corpus['date_created'])
        self.assertEquals(corpus['_id'], new_corpus._id)
        self.assertEquals(corpus['name'], new_corpus.name)
        self.assertEquals(corpus['slug'], new_corpus.slug)
        self.assertEquals(corpus['description'], new_corpus.description)
        self.assertEquals(corpus['owner'], new_corpus.owner)
        self.assertEquals(corpus['date_created'], new_corpus.date_created)
        self.assertEquals(corpus['last_modified'], new_corpus.last_modified)

    def test_get_existing_corpora(self):
        new_corpus = self.store.Corpus(name='Just Testing',
                                       owner=u'Álvaro Justen',
                                       description=u'This is just a test')
        new_corpus.save()
        same_corpus_1 = self.store.Corpus.find_by_id(new_corpus._id)
        same_corpus_2 = self.store.Corpus.find_by_name(new_corpus.name)
        same_corpus_3 = self.store.Corpus.find_by_slug(new_corpus.slug)
        self.assertEquals(new_corpus._id, same_corpus_1._id)
        self.assertEquals(new_corpus._id, same_corpus_2._id)
        self.assertEquals(new_corpus._id, same_corpus_3._id)

    def test_corpus_should_have_at_least_name(self):
        new_corpus = self.store.Corpus()
        with self.assertRaises(RuntimeError):
            new_corpus.save()
        self.assertEquals(self.corpora.find().count(), 0)

    def test_save_corpus_twice(self):
        new_corpus = self.store.Corpus(name='testing')
        new_corpus.save()
        new_corpus.owner = 'me'
        new_corpus.save()
        corpus = self.corpora.find_one()
        self.assertEquals(corpus['owner'], 'me')

    def test_get_all_corpora(self):
        for i in range(10):
            self.store.Corpus(name='testing-' + str(i)).save()
        counter = 0
        for corpus in self.store.Corpus.all:
            self.assertIn('_id', dir(corpus))
            self.assertIn('name', dir(corpus))
            self.assertTrue(corpus.name.startswith('testing-'))
            counter += 1
        self.assertEquals(counter, 10)

    def test_add_document(self):
        document = self.store.Document(filename='test.txt',
                                       owner=u'Álvaro Justen', corpora=[])
        document.save()
        documents = self.documents.find()
        self.assertEquals(documents.count(), 1)
        self.assertEquals(documents[0]['owner'], u'Álvaro Justen')
        self.assertEquals(documents[0]['corpora'], [])
        self.assertEquals(documents[0]['date_created'],
                          document.date_created)

    def test_document_should_have_at_least_filename(self):
        new_document = self.store.Document()
        with self.assertRaises(RuntimeError):
            new_document.save()
        self.assertEquals(self.documents.find().count(), 0)

    def test_document_set_and_get_blob(self):
        data = 'now is better than never'
        document = self.store.Document(filename='test.txt',
                                       owner=u'Álvaro Justen', corpora=[])
        document.save()
        document.set_blob(data)
        results = self.gridfs.list()
        self.assertEquals(len(results), 1)
        self.assertEquals(results[0], document._id)
        gridfs_file = self.gridfs.get_last_version(filename=document._id)
        self.assertEquals(gridfs_file.length, len(data))
        self.assertEquals(gridfs_file.read(), data)
        self.assertEquals(document.get_blob(), data)
