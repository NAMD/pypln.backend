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


import subprocess
import re
from pypln.backend.celery_task import PyPLNTask

SEMANTIC_TAGS = \
{
    'Animal':
        {
        '<A>': u'Animal, umbrella tag (clone, fêmea, fóssil, parasito, predador)' ,
        '<AA>': u'Group of animals (cardume, enxame, passarada, ninhada)',
        '<Adom>': u'Domestic animal or big mammal (likely to have female forms etc.: terneiro, leão/leoa, cachorro)',
        '<AAdom>': u'Group of domestic animals (boiada)',
        '<Aich>': u'Water-animal (tubarão, delfim)',
        '<Amyth>': u'Mythological animal (basilisco)',
        '<Azo>': u'Land-animal (raposa)',
        '<Aorn>': u'Bird (águia, bem-te-vi)',
        '<Aent>': u'Insect (borboleta)',
        '<Acell>': u'Cell-animal (bacteria, blood cells: linfócito)',
        },
    'Plant':
        {
        '<B>': u'Plant, umbrella tag',
        '<BB>': u'Group of plants, plantation (field, forest etc.: mata, nabal)',
        '<Btree>': u'Tree (oliveira, palmeira)',
        '<Bflo>': u'Flower (rosa, taraxaco)',
        '<Bbush>': u'Bush, shrub (rododendro, tamariz)',
        '<fruit>': u'(fruit, berries, nuts: maçã, morango, avelã, melancia)',
        '<Bveg>': u'(vegetable espargo, funcho)',
        },
    'Human':
        {
        '<H>': u'Human, umbrella tag',
        '<HH>': u'Group of humans (organisations, teams, companies, e.g. editora)',
        '<Hattr>': u'Attributive human umbrella tag (many -ista, -ante)',
        '<Hbio>': u'Human classified by biological criteria (race, age etc., caboclo, mestiço, bebé, adulto)',
        '<Hfam>': u'Human with family or other private relation (pai, noiva)',
        '<Hideo>': u'Ideological human (comunista, implies <Hattr>), also: follower, disciple (dadaista)',
        '<Hmyth>': u'Humanoid mythical (gods, fairy tale humanoids, curupira, duende)',
        '<Hnat>': u'Nationality human (brasileiro, alemão), also: inhabitant (lisboeta)',
        '<Hprof>': u'Professional human (marinheiro, implies <Hattr>), also: sport, hobby (alpinista)',
        '<Hsick>': u'Sick human (few: asmático, diabético, cp <sick>)',
        '<Htit>': u'Title noun (rei, senhora)',
        },
    'Place and spatial':
        {
        '<L>': u'Place, umbrella tag',
        '<Labs>': u'Abstract place (anverso. auge)',
        '<Lciv>': u'Civitas, town, country, county (equals <L> + <HH>, cidade, país)',
        '<Lcover>': u'Cover, lid (colcha, lona, tampa)',
        '<Lh>': u'Functional place, human built or human-used (aeroporto, anfiteatro, cp. <build> for just a building)',
        '<Lopening>': u'opening, hole (apertura, fossa)',
        '<Lpath>': u'Path (road, street etc.: rua, pista)' ,
        '<Lstar>': u'Star object (planets, comets: planeta, quasar)',
        '<Lsurf>': u'surface (face, verniz, cp. <Lcover>)',
        '<Ltip>': u'tip place, edge (pico, pontinha, cp. <Labs>)',
        '<Ltop>': u'Geographical, natural place (promontório, pântano)',
        '<Ltrap>': u'trap place (armadilha, armazelo)',
        '<Lwater>': u'Water place (river, lake, sea: fonte, foz, lagoa)',
        '<bar>': u'barrier noun (dique, limite, muralha)',
        '<build>': u'(building)',
        '<inst>': u'(institution)',
        '<pict>': u'(picture)',
        '<sit>': u'(situation)',
        '<pos-an>': u'anatomical/body position (few: desaprumo)',
        '<pos-soc>': u'social position, job (emprego, condado, capitania, presidência)',
        },
    'Vehicle':
        {
        '<V>': u'Vehicle, umbrella tag and ground vehicle (car, train: carro, comboio, tanque, teleférico)',
        '<VV>': u'Group of vehicles (armada, convoy: frota, esquadra)',
        '<Vwater>': u'Water vehicle (ship: navio, submersível, canoa)',
        '<Vair>': u'Air vehicle (plane: hidroplano, jatinho)',
        },
    'Abstract':
        {
        '<ac>': u'Abstract countable, umbrella tag (alternativa, chance, lazer)',
        '<ac-cat>': u'Category word (latinismo, número atômico)',
        '<ac-sign>': u'sign, symbol (parêntese, semicolcheia)',
        '<am>': u'Abstract mass/non-countable, umbrella tag (still contains many cases that could be <f-..>, e.g. habilidade, legalidade)',
        '<ax>': u'Abstract/concept, neither countable nor mass (endogamia), cp. <f>, <sit> etc.',
        '<f...>': u'(features)',
        '<dir>': u'direction noun (estibordo, contrasenso, norte)',
        '<geom...>': u'(shapes)',
        '<meta>': u'meta noun (tipo, espécie)',
        '<brand>': u'(MARCA) brand',
        '<genre>': u'(DISCIPLINA) subject matter',
        '<school>': u'(ESCOLA) school of thought',
        '<idea>': u'(IDEA) idea, concept',
        '<plan>': u'(PLANO) named plan, project',
        '<author>': u'(OBRA) artist-s name, standing for body of work',
        '<absname>': u'(NOME)',
        '<disease>': u'(ESTADO) physiological state, in particular: disease',
        },
    'Concept':
        {
        '<conv>': u'convention (social rule or law, lei, preceito)',
        '<domain>': u'subject matter, profession, cf. <genre>, anatomia, citricultura, dactilografia)',
        '<ism>': u'ideology or other value system (anarquismo, anti-ocidentalismo, apartheid)',
        '<genre>': u'',
        '<ling>': u'language (alemão, catalão, bengali)',
        '<disease>': u'',
        '<state...>': u'',
        '<therapy>': u'therapy (also <domain> and <activity>, acupuntura, balneoterapia)',
        },
    'Game':
        {
        '<game>': u'play, game (bilhar, ioiô, poker, also <activity>)',
        },
    'Genre':
        {
        '<genre>': u'genre (especially art genre, cf. <domain>, modernismo, tropicalismo)',
        },
    'Quantity':
        {
        '<unit>': u'',
        '<amount>': u'quantity noun (bocada, teor, sem-fim)',
        '<cur>': u'currency noun (countable, implies <unit>, cf. <mon>, dirham, euro, real, dólar)',
        '<mon>': u'amount of money (bolsa, custo, imposto, cf. <cur>)',
        },
    'Action':
        {
        '<act>': u'Action umbrella tag (+CONTROL, PERFECTIVE)',
        '<act-beat>': u'beat-action (thrashing, pancada, surra)',
        '<act-d>': u'do-action (typically dar/fazer + N, tentativa, teste, homenagem)',
        '<act-s>': u'speech act or communicative act (proposta, ordem)',
        '<act-trick>': u'trick-action (cheat, fraud, ruse, jeito, fraude, similar to <act-d>)',
        '<activity>': u'Activity, umbrella tag (+CONTROL, IMPERFECTIVE, correria, manejo)',
        '<sport>': u'',
        '<game>': u'',
        '<therapy>': u'',
        '<dance>': u'dance (both <activity>, <genre> and <sem-l>, calipso, flamenco, forró)',
        '<fight>': u'fight, conflict (also <activity> and +TEMP, briga, querela)',
        '<talk>': u'speech situation, talk, discussion, quarrel (implies <activity> and <sd>, entrevista, lero-lero)',
        },
    'Anatomical':
        {
        '<an>': u'Anatomical noun, umbrella tag (carótida, clítoris, dorso)',
        '<anmov>': u'Movable anatomy (arm, leg, braço, bíceps, cotovelo)',
        '<anorg>': u'Organ (heart, liver, hipófise, coração, testículo)',
        '<anost>': u'Bone (calcâneo, fíbula, vértebra)',
        '<anzo>': u'Animal anatomy (rúmen, carapaça, chifres, tromba)',
        '<anorn>': u'Bird anatomy (bico, pluma)',
        '<anich>': u'Fish anatomy (few: bránquias, siba)',
        '<anent>': u'Insect anatomy (few: tentáculo, olho composto)',
        '<anbo>': u'Plant anatomy (bulbo, caule, folha)',
        '<f-an>': u'(human anatomical feature)',
        },
    'Thing':
        {
        '<cc>': u'Concrete countable object, umbrella tag (briquete, coágulo, normally movable things, unlike <part-build>)',
        '<cc-h>': u'Artifact, umbrella tag (so far empty category in PALAVRAS)',
        '<cc-beauty>': u'ornamental object (few: guirlanda, rufo)',
        '<cc-board>': u'flat long object (few: board, plank, lousa, tabla)',
        '<cc-fire>': u'fire object (bonfire, spark, chispa, fogo, girândola)',
        '<cc-handle>': u'handle (garra, ansa, chupadouro)',
        '<cc-light>': u'light artifact (lampião, farol, projector) ',
        '<cc-particle>': u'(atomic) particle (few: cátion, eletrônio)',
        '<cc-r>': u'read object (carteira, cupom, bilhete, carta, cf. <sem-r>)',
        '<cc-rag>': u'cloth object (towel, napkin, carpet, rag) , cp. <mat-cloth>',
        '<cc-stone>': u'(cc-round) stones and stone-sized round objects (pedra, itá, amonite, tijolo)',
        '<cc-stick>': u'stick object (long and thin, vara, lançe, paulito)',
        '<object>': u'(OBJECT) named object',
        '<common>': u'(OBJECT) common noun used as name',
        '<mat>': u'(SUBSTANCIA) substance',
        '<class>': u'(CLASSE) classification category for things',
        '<plant>': u'(CLASSE) plant name',
        '<currency>': u'(MOEDA) currency name (also marked on the number)',
        '<mass>': u'mass noun (e.g. "leite", "a-gua")',
        '<furn>': u'furniture (cama, cadeira, tambo, quadro)',
        '<con>': u'container (implies <num+> quantifying, ampola, chícara, aquário)',
        },
    'Substance':
        {
        '<cm>': u'concrete mass/non-countable, umbrella tag, substance (cf. <mat>, terra, choça, magma)',
        '<cm-h>': u'human-made substance (cf. <mat>, cemento)',
        '<cm-chem>': u'chemical substance, also biological (acetileno, amônio, anilina, bilirrubina',
        '<cm-gas>': u'gas substance (so far few: argônio, overlap with. <cm-chem> and <cm>)',
        '<cm-liq>': u'liquid substance (azeite, gasolina, plasma, overlap with <food> and <cm-rem>)',
        '<cm-rem>': u'remedy (medical or hygiene, antibiótico, canabis, quinina, part of <cm-h>, overlap with <cm-chem>)',
        },
    'Materials':
        {
        '<mat>': u'material (argila, bronze, granito, cf. <cm>)',
        '<mat-cloth>': u'cloth material (seda, couro, vison, kevlar), cp. <cc-rag>',
        '<cord>': u'cord, string, rope, tape (previously <tool-tie>, arame, fio, fibrila)',
        },
    'Clothing':
        {
        '<cloA>': u'animal clothing (sela, xabraque)',
        '<cloH>': u'human clothing (albornoz, anoraque, babadouro, bermudas)',
        '<cloH-beauty>': u'beauty clothing (e.g. jewelry, diadema, pendente, pulseira)',
        '<cloH-hat>': u'hat (sombrero, mitra, coroa)',
        '<cloH-shoe>': u'shoe (bota, chinela, patim)',
        '<mat-cloth>': u'cloth material (seda, couro, vison, kevlar), cp. <cc-rag>',
        '<clo...>': u'(clothing)',
        },
    'Collective':
        {
        '<coll>': u'set,collective (random or systematic collection/compound/multitude of similar but distinct small parts, conjunto, série)',
        '<coll-cc>': u'thing collective, pile (baralho, lanço)',
        '<coll-B>': u'plant-part collective (buquê, folhagem)',
        '<coll-sem>': u'semantic collective, collection (arquivo, repertório)',
        '<coll-tool>': u'tool collective, set (intrumentário, prataria)',
        '<HH>': u'(group)',
        '<AA>': u'(herd)',
        '<BB>': u'(plantation)',
        '<VV>': u'(convoy)',
        },
    'Time_Event':
        {
        '<dur>': u'duration noun (test: durar+, implies <unit>, e.g. átimo, mês, hora)',
        '<temp>': u'temporal object, point in time (amanhecer, novilúnio, test: até+, cf. <dur> and <per>)',
        '<event>': u'non-organised event  (-CONTROL, PERFECTIVE, milagre, morte)',
        '<occ>': u'occasion, human/social event (copa do mundo, aniversário, jantar, desfile, cp. unorganized <event>) ',
        '<process>': u'process (-CONTROL, -PERFECTIVE, cp. <event>, balcanização, convecção, estagnação)',
        '<act...>': u'',
        '<activity>': u'',
        '<history>': u'(EFEMERIDE) one-time [historical] occurrence',
        '<date>': u'(DATA) date',
        '<hour>': u'(HORA) hour',
        '<period>': u'(PERIODO) period',
        '<cyclic>': u'(CICLICO) cyclic time expression',
        '<month>': u'month noun/name (agosto, julho, part of <temp>)',
        '<per>': u'period of time (prototypical test: durante, e.g. guerra, década, cf. <dur> and <temp>)',
        },
    'Feature':
        {
        '<f>': u'feature/property, umbrella tag (problematicidade, proporcionalidade)',
        '<f-an>': u'anatomical "local" feature, includes countables, e.g. barbela, olheiras)',
        '<f-c>': u'general countable feature (vestígio, laivos, vinco)',
        '<f-h>': u'human physical feature, not countable (lindura, compleição, same as <f-phys-h>, cp. anatomical local features <f-an>)',
        '<f-phys-h>': u'',
        '<f-psych>': u'human psychological feature (passionalidade, pavonice, cp. passing states <state-h>)',
        '<f-q>': u'quantifiable feature (e.g. circunferência, calor, DanGram-s <f-phys> covers both <f> and <f-q>)',
        '<f-phys>': u'',
        '<f-right>': u'human social feature (right or duty): e.g. copyright, privilégio, imperativo legal)',
        '<state>': u'',
        '<state-h>': u'(human state)',
        },
    'Food':
        {
        '<food>': u'natural/simplex food (aveia, açúcar, carne, so far including <spice>)',
        '<food-c>': u'countable food (few: ovo, dente de alho, most are <fruit> or <food-c-h>)',
        '<food-h>': u'human-prepared/complex culinary food (caldo verde, lasanha)',
        '<food-c-h>': u'culinary countable food (biscoito, enchido, panetone, pastel)',
        '<drink>': u'drink (cachaça, leite, guaraná, moca)',
        '<fruit>': u'fruit, berry, nut (still mostly marked as <food-c>, abricote, amora, avelã, cebola)',
        '<spice>': u'condiments, pepper',
        },
    'Part':
        {
        '<part>': u'distinctive or functional part (ingrediente, parte, trecho)',
        '<part-build>': u'structural part of building or vehicle (balustrada, porta, estai)',
        '<piece>': u'indistinctive (little) piece (pedaço, raspa)',
        '<cc-handle>': u'',
        '<Ltip>': u'',
        },
    'Perception':
        {
        '<percep-f>': u'what you feel (senses or sentiment, pain, e.g. arrepio, aversão, desagrado, cócegas, some overlap with <state-h>)',
        '<percep-l>': u'sound (what you hear, apitadela, barrulho, berro, crepitação)',
        '<percep-o>': u'olfactory impression (what you smell, bafo, chamuscom fragrância)',
        '<percep-t>': u'what you taste (PALAVRAS: not implemented)',
        '<percep-w>': u'visual impression (what you see, arco-iris, réstia, vislumbre)',
        },
    'Semantic Product':
        {
        '<sem>': u'semiotic artifact, work of art, umbrella tag (all specified in PALAVRAS)',
        '<sem-c>': u'cognition product (concept, plan, system, conjetura, esquema, plano, prejuízo)',
        '<sem-l>': u'listen-work (music, cantarola, prelúdio, at the same time <genre>: bossa nova)',
        '<sem-nons>': u'nonsense, rubbish (implies <sem-s>, galimatias, farelório)',
        '<sem-r>': u'read-work (biografia, dissertação, e-mail, ficha cadastral)',
        '<sem-s>': u'speak-work (palestra, piada, exposto)',
        '<sem-w>': u'watch-work (filme, esquete, mininovela)',
        '<ac-s>': u'(speach act)',
        '<talk>': u'',
        },
    'Disease':
        {
        '<sick>': u'disease (acne, AIDS, sida, alcoolismo, cp. <Hsick>)',
        '<Hsick>': u'',
        '<sick-c>': u'countable disease-object (abscesso, berruga, cicatriz, gangrena)',
        },
    'State-of-affairs':
        {
        '<sit>': u'psychological situation or physical state of affairs (reclusão, arruaça, ilegalidade, more complex and more "locative" than <state> and <state-h>',
        '<state>': u'state (of something, otherwise <sit>), abundância, calma, baixa-mar, equilíbrio',
        '<state-h>': u'human state (desamparo, desesperança, dormência, euforia, febre',
        '<f-psych>': u'',
        '<f-phys-h>': u'',
        },
    'Sport':
        {
        '<sport>': u'sport (capoeira, futebol, golfe, also <activity> and <domain>)',
        },
    'Tool':
        {
        '<tool>': u'tool, umbrella tag (abana-moscas, lápis, computador, maceta, "handable", cf. <mach>)',
        '<tool-cut>': u'cutting tool, knife (canivete, espada)',
        '<tool-gun>': u'shooting tool, gun (carabina, metralhadora, helicanão, in Dangram: <tool-shoot>)',
        '<tool-mus>': u'musical instrument (clavicórdio, ocarina, violão)',
        '<tool-sail>': u'sailing tool, sail (vela latina, joanete, coringa)',
        '<mach>': u'machine (complex, usually with moving parts, betoneira, embrulhador, limpa-pratos, cp. <tool>)',
        '<tube>': u'tube object (cânula, gasoduto, zarabatana, shape-category, typically with another category, like <an> or <tool>)',
        },
    'Unit':
        {
        '<unit>': u'unit noun (always implying <num+>, implied by <cur> and <dur>, e.g. caloria, centímetro, lúmen))',
        },
    'Weather':
        {
        '<wea>': u'weather (states), umbrella tag (friagem, bruma)',
        '<wea-c>': u'countable weather phenomenon (nuvem, tsunami)',
        '<wea-rain>': u'rain and other precipitation (chuvisco, tromba d-água, granizo)',
        '<wea-wind>': u'wind, storm (brisa, furacão)',
        },
    'Person':
        {
        '<hum>': u'(INDIVIDUAL) person name (cp. <H>)',
        '<official>': u'(CARGO) official function (~ cp. <Htitle> and <Hprof>)',
        '<member>': u'(MEMBRO) member',
        },
    'Organization_Group':
        {
        '<admin>': u'(ADMINISTRACAO, ORG.) administrative body (government, town administration etc.)',
        '<org>': u'(INSTITUICAO/EMPRESA) commercial or non-commercial, non-administrative non-party organisations (not place-bound, therefore not the same as <Linst>)',
        '<inst>': u'(EMPRESA) organized site (e.g. restaurant, cp. <Linst>)',
        '<media>': u'(EMPRESA) media organisation (e.g. newspaper, tv channel)',
        '<party>': u'(INSTITUICAO) political party',
        '<suborg>': u'(SUB) organized part of any of the above',
        '<company>': u'currently unsupported: (EMPRESA) company (not site-bound, unlike <inst>, now fused with. <org>)',
        },
    'Group':
        {
        '<groupind>': u'(GROUPOIND) people, family',
        '<groupofficial>': u'(GROUPOCARGO) board, government (not fully implemented)',
        '<grouporg>': u'currently unsupported (GROUPOMEMBRO) club, e.g. football club (now fused with <org>)',
        },
    'Place':
        {
        '<top>': u'(GEOGRAFICO) geographical location (cp. <Ltop>)',
        '<civ>': u'(ADMINISTRACAO, LOC.) civitas (country, town, state, cp. <Lciv>)',
        '<address>': u'(CORREIO) address (including numbers etc.)',
        '<site>': u'(ALARGADO) functional place (cp. <Lh>)',
        '<virtual>': u'(VIRTUAL) virtual place',
        '<astro>': u'(OBJECTO) astronomical place (in HAREM object, not place)',
        '<road>': u'suggested (ALARGADO) roads, motorway (unlike <address>)',
        },
    'Work_of_Art':
        {
        '<tit>': u'(REPRODUZIDO) [title of] reproduced work, copy',
        '<pub>': u'(PUBLICACAO) [scientific] publication',
        '<product>': u'(PRODUTO) product brand',
        '<V>': u'(PRODUTO) vehicle brand (cp. <V>, <Vair>, <Vwater>)',
        '<artwork>': u'(ARTE) work of art',
        '<pict>': u'picture (combination of <cc>, <sem-w> and <L>, caricatura, cintilograma, diapositivo)',
        },
    'Colours':
        {
        '<col>': u'colours',
        },
    'Numeric_and_Math':
        {
        '<quantity>': u'(QUANTIDADE) simple measuring numeral',
        '<prednum>': u'(CLASSIFICADO) predicating numeral',
        '<currency>': u'(MOEDA) currency name (also marked on the unit)',
        '<geom>': u'geometry noun (circle, shape, e.g. losango, octógono, elipse)',
        '<geom-line>': u'line (few: linha, percentil, curvas isobáricas)',
        },
    'Modifying_Adjectives':
        {
        '<jh>': u'adjective modifying human noun',
        '<jn>': u'adjective modifying inanimate noun ',
        '<ja>': u'adjective modifying animal',
        '<jb>': u'adjective modifying plant',
        '<col>': u'color adjective',
        '<nat>': u'nationality adjective (also: from a certain town etc.)',
        '<attr>': u'(human) attributive adjective (not fully implemented, cp. <Hattr>, e.g. "um presidente COMUNISTA")',
        },
    'Verbs_related_human_things':
        {
        '<vH>': u'verb with human subject',
        '<vN>': u'verb with inanimate subject',
        },
}


angle_brackets_contents = re.compile('(<[a-zA-Z]*>)')

class SemanticTagger(PyPLNTask):
    """Semantic Tagger"""

    def process(self, document):
        if not document['palavras_raw_ran']:
            # If palavras didn't run, just ignore this document
            return {}

        lines = document['palavras_raw'].split('\n')
        tagged_entities = {}
        for line in lines:
            if line.startswith('$') or not line.strip() or \
               line.strip() == '</s>':
                continue
            word = line.split()[0]
            word_sem_tags = angle_brackets_contents.findall(line.strip())
            is_tagged = False
            for tag in word_sem_tags:
                for category, subcategories in SEMANTIC_TAGS.items():
                    if tag in subcategories:
                        tagged_entities.setdefault(category, []).append(word)
                        is_tagged = True
            if not is_tagged:
                tagged_entities.setdefault('Non_Tagged', []).append(word)
        return {'semantic_tags': tagged_entities}
