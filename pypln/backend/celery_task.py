# coding: utf-8
#
# Copyright 2015 NAMD-EMAP-FGV
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
import pymongo
from celery import Task

# This import may look like an unused imported, but it is not.
# When our base task class is defined, the Celery app must have already been
# instantiated, otherwise when this code is imported elsewhere (like in a
# client that will call a task, for example) celery will fallback to the
# default app, and our configuration will be ignored. This is not an issue in
# the documented project layout, because there they import the app in the
# module that define the tasks (to use the decorator in `app.task`).
from pypln.backend.celery_app import app

from pypln.backend import config


mongo_client = pymongo.MongoClient(host=config.MONGODB_URIS)
database = mongo_client[config.MONGODB_DBNAME]
document_collection = database[config.MONGODB_COLLECTION]

class DocumentNotFound(Exception):
    pass

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
        document = document_collection.find_one({"_id": document_id})
        if document is None:
            raise DocumentNotFound('Document with ObjectId("{}") not found in '
                    'database'.format(document_id))
        result = self.process(document)
        document_collection.update({"_id": document_id}, {"$set": result})
        return document_id

    def process(self, document):
        """
        This process should be implemented by subclasses. It is responsible for
        performing the analysis itself. It will receive a dictionary as a
        paramenter (containing all the current information on the document)
        and must return a dictionary with the keys to be saved in the database.
        """
        raise NotImplementedError
