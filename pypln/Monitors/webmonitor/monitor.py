#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Web app to monitor PyPLN cluster

license: GPL v3 or later
__date__ = 5 / 13 / 12
"""

__docformat__ = "restructuredtext en"

import zmq
from flask import Flask,request, jsonify, make_response, render_template, flash, redirect, url_for, session, escape, g
from pymongo import Connection




app = Flask(__name__)
app.config.from_pyfile('monitor.cfg')

Db = Connection()[app.config['Database']]

@app.route("/")
def dashboard():
    with open("/tmp/pypln.log") as f:
        logs = f.readlines()
    logs.reverse() # Latest entries first
    return render_template('index.html',logs=logs)

def get_cluster_stats():
    """
    Return status data about the cluster, such as list of nodes, network status, overall load, etc.
    :return: JSON object with the data fetched from Mongodb
    """
    stats = Db.Stats.find().sort({"last_reported":-1})



if __name__ == "__main__":
    app.run()