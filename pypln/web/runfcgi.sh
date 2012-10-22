#!/bin/bash
PYPLN_HOME="/srv/pypln"
MINSPARE=2
MAXSPARE=4
FCGI_PORT="8080"
ERRLOG="$PYPLN_HOME/logs/fcgi_server.error"
OUTLOG="$PYPLN_HOME/logs/fcgi_server.out"

source "$PYPLN_HOME/project/bin/activate"
exec python manage.py runfcgi method=threaded minspare=$MINSPARE maxspare=$MAXSPARE daemonize=false host=127.0.0.1 port=$FCGI_PORT errlog=$ERRLOG outlog=$OUTLOG
