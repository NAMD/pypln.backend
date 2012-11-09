#!/bin/bash
#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN. You can get more information at: http://pypln.org/.
#
# PyPLN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPLN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPLN.  If not, see <http://www.gnu.org/licenses/>.

PYPLN_HOME="/srv/pypln"
MINSPARE=2
MAXSPARE=4
FCGI_PORT="8080"
ERRLOG="$PYPLN_HOME/logs/fcgi_server.error"
OUTLOG="$PYPLN_HOME/logs/fcgi_server.out"

source "$PYPLN_HOME/project/bin/activate"
exec python manage.py runfcgi method=threaded minspare=$MINSPARE maxspare=$MAXSPARE daemonize=false host=127.0.0.1 port=$FCGI_PORT errlog=$ERRLOG outlog=$OUTLOG
