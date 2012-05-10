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
import time
from collections import defaultdict




app = Flask(__name__)
app.config.from_pyfile('settings.py')

Db = Connection()[app.config['DATABASE']]

@app.route("/")
def dashboard():
    info = Db.Stats.find_one(fields=['cluster'])
    number_nodes = len(info['cluster'])
    with open("/tmp/pypln.log") as f:
        logs = f.readlines()
    logs.reverse() # Latest entries first
    return render_template('index.html',logs=logs,n_nodes = number_nodes,nrows=number_nodes/2,nnames=info['cluster'].keys())

@app.route("/_get_stats")
def get_cluster_stats():
    """
    Return status data about the cluster, such as list of nodes, network status, overall load, etc.
    :return: JSON object with the data fetched from Mongodb
    """
    stats = Db.Stats.find(fields=['cluster','active_jobs','time_stamp']).sort("time_stamp",-1).limit(100)
    e = []
    timeseries = defaultdict(lambda:{}) #using a dictionary here to eliminate messages from the same second
    ts = defaultdict(lambda:[])
    for d in stats:
        for k,v in d['cluster'].iteritems():
            timeseries[k][int(d['time_stamp'])*1000]=[v['last_report']['status']['cpu'],v['last_report']['status']['memory']]
    for k,v in timeseries.iteritems():
        ts[k].append({'data':zip([(i,v[i][0]) for i in sorted(v.keys())]),
                      'label':"Percent CPU",
                      'color':"blue"
                      })
        ts[k].append({'data':zip([(i,v[i][1]) for i in sorted(v.keys())]),
                      'label':"Percent Memory",
                      'color':"red"
        })

        d.pop('_id')
#        d.pop('time_stamp')
        e.append(d)
    return json.dumps(ts)#jsonify(entries= e)

@app.route("/_get_logs")
def get_logs():
    """
    Get log entries from Mongo and return in a JSON object
    :return: JSON object
    """
    logs = Db.logs.find(fields=['timestamp','loggerName','level','message']).sort("timestamp",-1).limit(10)
    l = []
    for i in logs:
        i.pop('_id')
        #converting to javascript timestamps which are in milisecconds
        i['timestamp'] = time.mktime(i['timestamp'].as_datetime().timetuple())*1000
        l.append(i)
    return jsonify(logs=l)


def main():
    app.run()

if __name__ == "__main__":
    main()