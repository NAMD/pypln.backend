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


app = Flask(__name__)
app.config.from_pyfile('monitor.cfg')

@app.route("/")
def dashboard():
    return render_template('index.html')


if __name__ == "__main__":
    app.run()