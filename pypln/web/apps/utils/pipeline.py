# coding: utf-8
#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN.
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

from pypelinin import Job, Pipeline, PipelineManager, Client


default_pipeline = {Job('Extractor'): Job('Tokenizer'),
                    Job('Tokenizer'): (Job('POS'), Job('FreqDist')),
                    Job('FreqDist'): Job('Statistics')}

def create_pipeline(api, broadcast, data, timeout):
    pipeline = Pipeline(default_pipeline, data=data)
    manager = PipelineManager(api, broadcast)
    return manager.start(pipeline)


def get_config_from_router(api, timeout=5):
    client = Client()
    client.connect(api)
    client.send_api_request({'command': 'get configuration'})
    if client.api_poll(timeout):
        result = client.get_api_reply()
    else:
        result = None
    client.disconnect()
    return result

