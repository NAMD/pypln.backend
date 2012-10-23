# coding: utf-8

from pypelinin import Job, Pipeline, PipelineManager, Client


default_pipeline = {Job('Extractor'): Job('Tokenizer'),
                    Job('Tokenizer'): (Job('POS'), Job('FreqDist')),
                    Job('FreqDist'): Job('Statistics')}

def create_pipeline(api, broadcast, data, timeout):
    pipeline = Pipeline(default_pipeline, data=data)
    manager = PipelineManager(api, broadcast)
    return manager.start(pipeline)


def get_config_from_manager(api, timeout=5):
    client = Client()
    client.connect(api)
    client.send_api_request({'command': 'get configuration'})
    if client.api_poll(timeout):
        result = client.get_api_reply()
    else:
        result = None
    client.disconnect()
    return result

