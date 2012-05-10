#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Web app to monitor PyPLN cluster

license: GPL v3 or later
__date__ = 5 / 13 / 12
"""

__docformat__ = "restructuredtext en"

import zmq
from flask import Flask,request, jsonify,json, make_response, render_template, flash, redirect, url_for, session, escape, g
from pymongo import Connection
import datetime




app = Flask(__name__)
app.config.from_pyfile('settings.py')

Db = Connection()[app.config['DATABASE']]

@app.route("/")
def dashboard():
    with open("/tmp/pypln.log") as f:
        logs = f.readlines()
    logs.reverse() # Latest entries first
    return render_template('index.html',logs=logs)

@app.route("/_get_stats")
def get_cluster_stats():
    """
    Return status data about the cluster, such as list of nodes, network status, overall load, etc.
    :return: JSON object with the data fetched from Mongodb
    """
    stats = Db.Stats.find(fields=['cluster','active_jobs']).sort("time_stamp",-1)
    e = []
    for d in stats:
        d.pop('_id')
#        d.pop('time_stamp')
        e.append(d)
    return jsonify(entries= e)

@app.route("/_get_logs")
def get_logs():
    """
    Get log entries from Mongo and return in a JSON object
    :return: JSON object
    """
    logs = Db.logs.find(fields=['asctime','loggerName','level','message']).sort("timestamp",-1).limit(10)
    l = []
    for i in logs:
        i.pop('_id')
        i['asctime'] = i['asctime'].split(',')[0].strip()
        l.append(i)
    return jsonify(logs=l)


def main():
    app.run()

if __name__ == "__main__":
    main()