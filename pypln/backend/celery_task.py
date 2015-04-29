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

from celery import Task

from pypln.backend.mongodict_adapter import MongoDictAdapter

# This import may look like an unused imported, but it is not.
# When our base task class is defined, the Celery app must have already been
# instantiated, otherwise when this code is imported elsewhere (like in a
# client that will call a task, for example) celery will fallback to the
# default app, and our configuration will be ignored. This is not an issue in
# the documented project layout, because there they import the app in the
# module that define the tasks (to use the decorator in `app.task`).
from pypln.backend.celery_app import app

from pypln.backend import config


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
                database=config.MONGODB_CONFIG['database'])
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
