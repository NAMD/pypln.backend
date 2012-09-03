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
from pypln.client import ManagerClient
from flask_debugtoolbar import DebugToolbarExtension

global Db

app = Flask(__name__)
app.debug = True
# set a 'SECRET_KEY' to enable the Flask session cookies
app.config['SECRET_KEY'] = 'ldfaoiwjeclgnasyghiwuasdggoer'
toolbar = DebugToolbarExtension(app)


@app.route("/")
def dashboard():
    """
    Fetch data about cluster resource usage.
    :return:
    """
    results = fetch_x_minutes(100)
    # Summing up resources
    resources, nnames = format_resources(results)

    return render_template('index.html',logs=[],
        n_nodes = len(nnames),
        nrows = len(nnames)/2,
        nnames = [n.replace('.',' ') for n in nnames],
        resources = resources,
    )

def fetch_x_minutes(x=100):
    """
    Fetch x minutes of data from the pypln.monitoring collection
    :param x: number of minutes to fetch
    :return:list of dictionaries
    """
    now  = time.time()
    last_time_to_check = now - x*60 #100 * time_between_measures
    match = {'timestamp': {'$gt': last_time_to_check}}
    selected_fields = {'host.network.cluster ip': 1, 'timestamp': 1}
    broker_ips = list(Db.monitoring.find(match, {'host.network.cluster ip': 1})\
    .distinct('host.network.cluster ip'))

    q = Db.monitoring.find(spec={},sort=[('timestamp',-1)]).limit(x)
    res = list(q)
    return res, broker_ips

def format_resources(status):
    """
    From the list of objects returned from Mongodb,
    returns a formatted dictionary of cluster resources
    :param status:
    :return: dictionary of resources
    """
    nnames = status[1]
    hosts = {h['host']['network']['cluster ip']: h['host'] for h in status[0]}

    resources = {'nodes':len(nnames),'cpus':0,'memory':0}
    resources['cpus'] += sum(h['cpu']["number of cpus"] for h in hosts.itervalues())
    resources['memory'] += sum(h['memory']['total'] for h in hosts.itervalues())
    return resources, nnames

@app.route("/_get_stats")
def get_cluster_stats():
    """
    Return status data about the cluster, such as list of nodes, network status, overall load, etc.
    :return: JSON object with the data fetched from Mongodb
    """
    results,ips = fetch_x_minutes(100)
    timeseries = defaultdict(lambda: {}) #using a dictionary here to eliminate messages from the same second
    ts = defaultdict(lambda: [])

    for h in results:
        ip = h['host']['network']['cluster ip'].replace('.',' ')
        timeseries[ip][int(h['timestamp'])*1000]=[h['host']['cpu']['cpu percent'],
                                                      h['host']['memory']['real percent']]
    for k,v in timeseries.iteritems():
        ts[k].append({'data':[(i,v[i][0]) for i in sorted(v.keys())],
                      'label':"Percent CPU",
                      'hoverable': True,
#                      'color':"blue"
                      })
        ts[k].append({'data':[(i,v[i][1]) for i in sorted(v.keys())],
                      'label':"Percent Memory",
                      'hoverable': True,
#                      'color':"red"
        })
    return json.dumps(ts)

def fetch_last_jobs():
    now  = time.time()
    last_time_to_check = now - 600 #last ten minutes
    match = {}#{'timestamp': {'$gt': last_time_to_check}}
    broker_ips = list(Db.monitoring.find(match, {'host.network.cluster ip': 1}).limit(1000)\
    .distinct('host.network.cluster ip'))
    jobs = {}
    for broker_ip in broker_ips:
        match = {'processes':{'$ne':[]},
             'host.network.cluster ip': broker_ip}
        fields = {'processes':1}
        result = list(Db.monitoring.find(match,fields=fields).limit(1))
        jobs[broker_ip] = result[0]['processes']
    return jobs

@app.route("/_get_active_jobs")
def get_jobs():
    """
    Returns a list of active jobs
    :return:JSON
    """
    jobs = fetch_last_jobs()
#    results,ips = fetch_x_minutes(5)
#    ajobs = set([])
#    for d in results:
#        for p in d['processes']:
#            ajobs.add(p['type']+" "+str(p['pid']))
    return json.dumps(jobs)

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

@app.route("/_test")
def test():
    return render_template('webmon-test.html')

def main():
    global Db
    app.config.from_pyfile('settings.py')
    conf = get_conf(app.config['MANAGER_URI'])
    Db = Connection(*conf)[app.config['DATABASE']]
    app.run()

if __name__ == "__main__":
    main()
