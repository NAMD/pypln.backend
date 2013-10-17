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
NER_SHA1SUM="1589ac1b477a7894ca98d783d27c5b5b73f51d3d  stanford-ner-2013-06-20.zip"

DOWNLOAD_URL="http://nlp.stanford.edu/software/$NER_DIRNAME.zip"
ANSWER="Y"
read -p "download Stanford NER? [Y/n] " ANSWER
if [ "$ANSWER" = "y" -o "$ANSWER" = "Y" ]
then
    cd "$SCRIPT_PATH"
    wget -c "$DOWNLOAD_URL"
    if [ "$(sha1sum $NER_DIRNAME.zip)" != "$NER_SHA1SUM" ]
    then
        echo "Something is wrong. NER zip file is different from expected."
        exit 1
    fi
    unzip -x $NER_DIRNAME.zip
else
    exit 1
fi
