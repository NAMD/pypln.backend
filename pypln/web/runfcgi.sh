#!/bin/bash
MINSPARE=2
MAXSPARE=4
FCGI_PORT="8080"
ERRLOG="$HOME/logs/fcgi_server.error"
OUTLOG="$HOME/logs/fcgi_server.out"

python manage.py runfcgi method=threaded minspare=$MINSPARE maxspare=$MAXSPARE daemonize=false host=127.0.0.1 port=$FCGI_PORT errlog=$ERRLOG outlog=$OUTLOG
