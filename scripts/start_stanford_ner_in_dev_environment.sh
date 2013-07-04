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


SCRIPT_PATH=$(dirname $(readlink -f $0))/

NER_DIRNAME="stanford-ner-2013-06-20"

NER_DIR="$SCRIPT_PATH/$NER_DIRNAME"

NER_PORT=4242
NER_CLASSIFIER="classifiers/english.muc.7class.distsim.crf.ser.gz"

cd "$NER_DIR"
exec java -mx500m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer -port $NER_PORT -loadClassifier "$NER_CLASSIFIER"
