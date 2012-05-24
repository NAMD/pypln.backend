#-*- coding:utf-8 -*-
"""
Main Pypln command line interface serves to host subcommands related to all apps
Created on 24/05/12
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'


import argparse
import extractor

def main():
    parser = argparse.ArgumentParser(prog=__name__)
    subparsers = parser.add_subparsers(title="subcommands",
        description="valid PyPLN subcommands",
        help="Type pypln subcommand --help for help on subcommands"
    )

    # Document Extractor Parser
    parser_extractor = subparsers.add_parser("extractor", description='Scans a directory tree or gridfs distributed file system looking for files to convert to text')
    parser_extractor.add_argument('-H', '--host', default='127.0.0.1', help='Host ip of the MongoDB server.')
    parser_extractor.add_argument('-d', '--db', required=True, help='Database in which to deposit the texts')
    parser_extractor.add_argument('-c', '--col', required=True, help="Collection in which to deposit the texts")
    parser_extractor.add_argument('-g', '--gfs', action='store_true',help="Scan griGridFS under db. ignores path")
    parser_extractor.add_argument('path', metavar='p', type=directory, help="Path of directory to scan for documents")
    parser_extractor.set_defaults(func=extractor.main)


    # Call the subcommand
    args = parser.parse_args()
    args.func(args)

if __name__=="__main__":
    main()
