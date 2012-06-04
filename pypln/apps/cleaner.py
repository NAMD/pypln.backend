#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
This script contains a number of cleanup functions
which are intended to be run as a cron job
with arguments indicating the type of cleanup to do.
"""

import argparse
from pypln.stores import filestor
from pypln.stores.mongostore import collection


def remove_blank_documents(db, coll):
    """Remove documents from database which have empty 'text' fields"""
    results = collection(db, coll).find({"text": ""},  fields=["_id"])
    for r in results:
        collection(db, coll).remove({'_id': r['_id']})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Perform some cleanup on database')
    parser.add_argument('--prune', '-p', choices=['empty', 'old'],
                        help="Removes faulty documents from database (empty etc)")
    args = parser.parse_args()
    if args.prune == 'empty':
        remove_blank_documents()
