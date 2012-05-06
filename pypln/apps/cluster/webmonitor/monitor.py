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
from mongoengine import connect

connect('pypln_cluster_stats')


app = Flask(__name__)
app.config.from_pyfile('monitor.cfg')

@app.route("/")
def dashboard():
    with open("/tmp/pypln.log") as f:
        logs = f.readlines()
    return render_template('index.html',logs=logs)


if __name__ == "__main__":
    app.run()