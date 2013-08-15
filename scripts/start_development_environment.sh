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
# along with PyPLN. If not, see <http://www.gnu.org/licenses/>.

SCRIPT_PATH=$(dirname $(readlink -f $0))/../ # get parent directory

# Adding the current directory to PYTHONPATH, the broker will be able to import
# pypln.backend even if the package is not installed
export PYTHONPATH="$SCRIPT_PATH:$PYTHONPATH"

echo "+-------------------------------------------------------+"
echo "|     This script is intended for development only.     |"
echo "| Please do not use it to run a production environment. |"
echo "+-------------------------------------------------------+"

echo "Starting Stanford NER..."
NER_DIRNAME="stanford-ner-2013-06-20"
NER_DIR="$SCRIPT_PATH/scripts/$NER_DIRNAME"
if [ -d "$NER_DIR" ]
then
    "$SCRIPT_PATH/scripts/start_stanford_ner_in_dev_environment.sh" &
    NER_PID=$!
    echo "Stanford NER has PID $NER_PID"
else
    echo "Can't find Stanford NER."
    echo "Run $SCRIPT_PATH/scripts/download_stanford_ner.sh to download it."
    exit 0
fi

echo "Starting router..."
"$SCRIPT_PATH/pypln/backend/router.py" &
ROUTER_PID=$!
echo "Router has PID $ROUTER_PID"

echo "Starting pipeliner..."
"$SCRIPT_PATH/pypln/backend/pipeliner.py" &
PIPELINER_PID=$!
echo "Pipeliner has PID $PIPELINER_PID"

echo "Starting broker..."
"$SCRIPT_PATH/pypln/backend/broker.py" &
BROKER_PID=$!
echo "Broker has PID $BROKER_PID"

trap "kill 0; exit" SIGINT SIGTERM SIGKILL

while :
do
    sleep 1
done
