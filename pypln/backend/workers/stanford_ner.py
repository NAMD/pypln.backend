# coding: utf-8
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

from pypelinin import Worker
import ner

NER_HOST="localhost"
NER_PORT=4242

class NERWrapper(ner.SocketNER):

    def __slashTags_parse_entities(self, tagged_text):
        """Return a list of token tuples (entity_type, token) parsed
        from slashTags-format tagged text.

        :param tagged_text: slashTag-format entity tagged text
        """
        return (match.groups()[::-1] for match in
            ner.client.SLASHTAGS_EPATTERN.finditer(tagged_text))

    def get_entities_as_tuples(self, text):
        """
        """
        if self.oformat != 'slashTags':
            raise NotImplementedError("get_entities_as_tuples is not "
                    "implemented for output formats other than slashTags")
        tagged_text = self.tag_text(text)
        entities = self.__slashTags_parse_entities(tagged_text)
        return entities

class StanfordNER(Worker):
    requires = ['text']

    def process(self, document):
        text = document['text']
        tagger = NERWrapper(host=NER_HOST,
                port=NER_PORT, output_format="slashTags")

        entities = list(tagger.get_entities_as_tuples(text.encode('utf-8')))

        return {'named_entities': entities}
