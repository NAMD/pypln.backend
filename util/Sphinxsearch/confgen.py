# -*- coding: utf-8 -*-
"""
Module implementing sphinxsearch conf file generation
"""
__author__ = 'fccoelho'

from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('pypln', 'templates'))


def get_conf(sources, indices):
    """
    Generates a sphinxsearch configuration file to drive indexing of databases
    examples arguments:
    sources = [{'name':'mongo1',
                'type':'xmlpipe2',
                #keys below for mysql type
                'host':'localhost',
                'user':'user',
                'password':'assword',
                'database':'mydatab',
                'port':3306,
                'sql_query':'select * from my_table'
                },{...}]
    indices = [{'source':'mongo1',
                'path':'/tmp/index',
                'html_strip':True,
                },{...}]
    :param sources: List of dictionaries with specs for the source (database to be indexed)
    :param indices: List of dictionaries with specs for  the index
    :return: configuration file as a string ready to be saved and used
    """
    template = env.get_template('sphinx-mongo-template.conf')
    return template.render(sources=sources, indices=indices)

