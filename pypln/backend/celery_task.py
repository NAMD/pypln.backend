from celery import Task

from pypln.backend.mongodict_adapter import MongoDictAdapter

DATABASE_NAME = 'test_pypln_backend'

class PyPLNTask(Task):
    """
    A base class for PyPLN tasks. It is in charge of getting the document
    information based on the document id (that should be passed as an argument
    by Celery), calling the `process` method, and saving this information on
    the database. It will also return the document id, so the rest of the
    pipeline has access to it.
    """

    def run(self, document_id):
        """
        This method is called by Celery, and should not be overridden.
        It will call the `process` method with a dictionary containing all the
        document information and will update de database with results.
        """
        document = MongoDictAdapter(doc_id=document_id,
                database=DATABASE_NAME)
        # Create a dictionary out of our document. We could simply pass
        # it on to the process method, but for now we won't let the user
        # manipulate the MongoDict directly.
        dic = {k: v for k, v in document.iteritems()}
        result = self.process(dic)
        document.update(result)
        return document_id

    def process(self, document):
        """
        This process should be implemented by subclasses. It is responsible for
        performing the analysis itself. It will receive a dictionary as a
        paramenter (containing all the current information on the document)
        and must return a dictionary with the keys to be saved in the database.
        """
        raise NotImplementedError
