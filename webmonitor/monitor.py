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
import argparse
from pypln.client import ManagerClient

global Db

app = Flask(__name__)

@app.route("/")
def dashboard():
    """
    Fetch data about cluster resource usage.
    :return:
    """
    now  = time.time()
#    pipeline = [{'$match':{'host.timestamp':{'$gt':now-600}}},
#                {'$sort':{'host.timestamp':-1}},
#                {'$project':{'host':1,}}
#    ]
#    q = Db.command('aggregate','monitoring',pipeline=pipeline)
    q = Db.monitoring.find({'host.timestamp':{'$gt':now-600}},sort=[('host.timestamp',-1)])

    results = list(q)


    # Summing up resources
    resources, nnames = format_resources(results)

    return render_template('index.html',logs=[],
        n_nodes = len(nnames),
        nrows = len(nnames)/2,
        nnames = list(nnames),
        resources = resources,
    )

def format_resources(status):
    """
    From the list of objects returned from Mongodb,
    returns a formatted dictionary of cluster resources
    :param status:
    :return: dictionary of resources
    """
    nnames = set([h['network']['cluster ip'][0] for h in status])
    resources = {'nodes':len(nnames),'cpus':0,'memory':0}
    for h in status:
        resources['cpus'] += h['host']['cpu']["number of cpus"]
        resources['memory'] += h['host']['memory']['total']
    return resources, nnames

@app.route("/_get_stats")
def get_cluster_stats():
    """
    Return status data about the cluster, such as list of nodes, network status, overall load, etc.
    :return: JSON object with the data fetched from Mongodb
    """
    stats = Db.Stats.find(fields=['cluster', 'active_jobs', 'time_stamp']).sort("time_stamp", -1).limit(100)
    e = []
    timeseries = defaultdict(lambda: {}) #using a dictionary here to eliminate messages from the same second
    ts = defaultdict(lambda: [])
    for d in stats:
        for k,v in d['cluster'].iteritems():
            timeseries[k][int(d['time_stamp'])*1000]=[v['last_report']['status']['cpu']*100,v['last_report']['status']['memory']*100]
    for k,v in timeseries.iteritems():
        ts[k].append({'data':zip([(i,v[i][0]) for i in sorted(v.keys())]),
                      'label':"Percent CPU",
#                      'color':"blue"
                      })
        ts[k].append({'data':zip([(i,v[i][1]) for i in sorted(v.keys())]),
                      'label':"Percent Memory",
#                      'color':"red"
        })

        d.pop('_id')
#        d.pop('time_stamp')
        e.append(d)
    return json.dumps(ts)#jsonify(entries= e)

@app.route("/_get_active_jobs")
def get_jobs():
    """
    Returns a list of active jobs
    :return:JSON
    """
    status = Db.monitoring.find_one(fields=['active jobs', 'time_stamp'], sort=[("time_stamp", -1)])
    return jsonify(jobs=status['active jobs'])

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
        i['timest'] = i['timestamp'].as_datetime().isoformat()
        i.pop('timestamp')
        l.append(i)
    return json.dumps(l)

def get_conf(args):
    """
    Fetches the Mongodb Configuration from manager
    :return:
    """
    host = '127.0.0.1'
    port = 27017
    client = ManagerClient(None, "Monitor")
    try:
        client.connect((args.manager,args.api))
        client.manager_api.send_json({'command': 'get configuration'})
        config = client.manager_api.recv_json()
    except: #TODO: handle manager not being alive here
        pass
    return host,port

def main():
    global Db
    app.config.from_pyfile('settings.py')
    conf = get_conf(app.config['MANAGER_URI'])
    Db = Connection(*conf)[app.config['DATABASE']]
    app.run()

if __name__ == "__main__":
    main()
