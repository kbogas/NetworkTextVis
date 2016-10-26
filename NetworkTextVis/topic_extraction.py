# -*- coding: utf-8 -*-

from bson.json_util import loads,dumps
from collections import defaultdict
from gensim import corpora,models
import networkx as nx 
import ConfigParser

def topic_extract(documents, strmodel='LDA'):
    stoplist = set('a able about above abst accordance according accordingly across act actually added adj affected affecting affects after afterwards again against ah all almost alone along already also although always am among amongst an and announce another any anybody anyhow anymore anyone anything anyway anyways anywhere apparently approximately are aren arent arise around as aside ask asking at auth available away awfully b back be became because become becomes becoming been before beforehand begin beginning beginnings begins behind being believe below beside besides between beyond biol both brief briefly but by c ca came can cannot can\'t cause causes certain certainly co com come comes contain containing contains could couldnt d date did didn\'t different do does doesn\'t doing done don\'t down downwards due during e each ed edu effect eg eight eighty either else elsewhere end ending enough especially et et-al etc even ever every everybody everyone everything everywhere ex except f far few ff fifth first five fix followed following follows for former formerly forth found four from further furthermore g gave get gets getting give given gives giving go goes gone got gotten h had happens hardly has hasn\'t have haven\'t having he hed hence her here hereafter hereby herein heres hereupon hers herself hes hi hid him himself his hither home how howbeit however hundred i id ie if i\'ll im immediate immediately importance important in inc indeed index information instead into invention inward is isn\'t it itd it\'ll its itself i\'ve j just k keep 	 keeps kept kg km know known knows l largely last lately later latter latterly least less lest let lets like liked likely line little \'ll look looking looks ltd m made mainly make makes many may maybe me mean means meantime meanwhile merely mg might million miss ml more moreover most mostly mr mrs much mug must my myself n na name namely nay nd near nearly necessarily necessary need needs neither never nevertheless new next nine ninety no nobody non none nonetheless noone nor normally nos not noted nothing now nowhere o obtain obtained obviously of off often oh ok okay old omitted on once one ones only onto or ord other others otherwise ought our ours ourselves out outside over overall owing own p page pages part particular particularly past per perhaps placed please plus poorly possible possibly potentially pp predominantly present previously primarily probably promptly proud provides put q que quickly quite qv r ran rather rd re readily really recent recently ref refs regarding regardless regards related relatively research respectively resulted resulting results right run s said same saw say saying says sec section see seeing seem seemed seeming seems seen self selves sent seven several shall she shed she\'ll shes should shouldn\'t show showed shown showns shows significant significantly similar similarly since six slightly so some somebody somehow someone somethan something sometime sometimes somewhat somewhere soon sorry specifically specified specify specifying still stop strongly sub substantially successfully such sufficiently suggest sup sure a about above after again against all am an and any are aren\'t as at be because been before being below between both but by can\'t cannot could couldn\'t did didn\'t do does doesn\'t doing don\'t down during each few for from further had hadn\'t has hasn\'t have haven\'t having he he\'d he\'ll he\'s her here here\'s hers herself him himself his how how\'s i i\'d i\'ll i\'m i\'ve if in into is isn\'t it it\'s its itself let\'s me more most mustn\'t my myself no nor not of off on once only or other ought our ours ourselves out over own same shan\'t she she\'d she\'ll she\'s should shouldn\'t so some such than that that\'s the their theirs them themselves then there there\'s these they they\'d they\'ll they\'re they\'ve this those through to too under until up very was wasn\'t we we\'d we\'ll we\'re we\'ve were weren\'t what what\'s when when\'s where where\'s which while who who\'s whom why why\'s with won\'t would wouldn\'t you you\'d you\'ll you\'re you\'ve your yours yourself yourselves fuck fucking lol shit'.split())
    texts = [[word for word in document.lower().split() if word not in stoplist] for document in documents]
    print texts
    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1
    texts = [[token for token in text if frequency[token] > 1] for text in texts]
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    if strmodel == "LDA":
        print 'Starting LDA......'
        mod = models.ldamodel.LdaModel(corpus, num_topics=10, id2word=dictionary)
    else:
        print 'Starting LDA mallet......'
        mod = models.wrappers.ldamallet.LdaMallet('mallet-2.0.8RC3/bin/mallet',corpus, num_topics=config.get('topic','topic_num'),  id2word=dictionary)
    probable_words = []
    print 'Computing probable words......'
    probable_words = []
    for i in range(0, 10):
        probable_words.append(mod.show_topic(i, int(10)))
    print 'Computing topic distribution....'
    if strmodel == 'LDA':
        mod.minimum_probability = 0.0
        dt = mod.get_document_topics(corpus,minimum_probability=0.0)
        final_dt = []
        for doc in dt:
            final_dt.append([(a[0],a[1]) for a in doc])
    else:
        final_dt = []
        for doc in documents:
            user_texts = dictionary.doc2bow([doc])
            final_dt.append(mod[user_texts])
    return final_dt, probable_words

def graph_cleansing(graph):
    G=nx.DiGraph()
    for node in list(graph.nodes()):
        G.add_node(node)
    for edge in list(graph.edges()):
        G.add_edge(*edge)
    return G
        
