import gensim
import numpy
import math
import networkx
from sklearn.feature_extraction.text import CountVectorizer
import regex as re
from HTMLParser import HTMLParser
import logging
from ranking import graph_influence


logger = logging.getLogger('universal_logger')


# --------------------- preprocessing methods --------------------------
# all these methods modify the data in place. They expect a mutable iterable
# containing the texts as an input


# regexps to capture hashtags - replies and urls
URLREGEX = re.compile(r'(?P<all>\s?(?P<url>(https?|ftp)://[^\s/$.?#].[^\s]*))')
HASHREGEX = re.compile(r'(?<=\s+|^)(?P<all>#(?P<content>\w+))', re.UNICODE)
REPLYREGEX = re.compile(r'(?P<all>(^|\s*)@(?P<content>\w+)\s*?)', re.UNICODE)


# used to strip html from text
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

def clean_html(X):
    """ Strip html

    :texts: collection - the collection of texts to change
    :returns: list of texts cleaned from html

    """
    return [re.sub('(\\<.*?\\>)','',text) for text in X if text!=None]

def detwittify(X):
    """ remove characteristics which aren't "natural" text
        hashtags, urls and usernames

    :texts: collection - the iterable of collection to change
    :returns: list of texts cleaned from twitter specific text

    """


    output = []
    for text in X:
        # remove urls from text
        cleaned = URLREGEX.sub('', text)
        # replace hashtags with the text of the tag
        cleaned = HASHREGEX.sub('\g<2>', cleaned)
        # replace @ tags
        cleaned = REPLYREGEX.sub('', cleaned)
        output.append(cleaned.strip())

    return output


def remove_numbers(X):
    return [re.sub('[0-9]+', ' ', text) for text in X]

def remove_punctuation(X):
    return [re.sub('[^\P{P}]+', ' ', text) for text in X]




def preprocess(X):
    # Choose what to use from the above processes

    # print '    -Cleaning html'
    X = clean_html(X)
    # print '    -Detwittifying'
    X = detwittify(X)
    # print '    -Removing Numbers'
    X = remove_numbers(X)
    # print '    -Removing Punctuation'
    X = remove_punctuation(X)
    return X





def nfm_extraction(texts, config):
    """Performs LDA topic modeling using the lda library

    Args:
        -texts (list): list of strings documents
        -config: Config object from main file

    Returns:
        -final_dt (list of lists): topic distributions for each document
        -dt: topic distributions for each document, in gensim 
            Transformed Corpus format
        -X: sparse numpy array from count_vectorizer. Document-Term Matrix
            essentially 
        -vocab: numpy_array with each word of the vocabulary
        -probable_words: vocabulary for the most probable words for each topic
            - 'keywords': list of the most probable words
            - 'topicId' : 'topic_0', ... topic identifier
    """

    # Preprocessing
    preprocessed_docs = preprocess(texts) 
    # Vectorizer
    params = dict(config.items('vectorizer'))
    for key in params.keys():
        if key == 'max_df':
            params[key] = float(params[key])
        if key == 'min_df':
            params[key] = int(params[key])
    vectorizer = CountVectorizer(**params)
    X = vectorizer.fit_transform(preprocessed_docs)
    # Sparse vectors to gensim format. 
    corpus = gensim.matutils.Sparse2Corpus(X, documents_columns=False)
    
    # The same for the dictionary
    dictionary = {}
    for key, val in vectorizer.vocabulary_.items():
        dictionary[val] = key
    #print len(dictionary.keys())
    # Train lda model
    vocab = numpy.array(vectorizer.get_feature_names())

    #  LDA model
    #dictionary = gensim.corpora.Dictionary(texts)
    #corpus = [dictionary.doc2bow(text) for text in texts]
    logger.info('Computing LDA topics...')
    ldamodel = gensim.models.ldamodel.LdaModel(corpus,
                                        num_topics=int(config.get('topic', 'num_topics')),
                                        id2word = dictionary,
                                        update_every=int(config.get('topic', 'update_every')),
                                        chunksize=int(config.get('topic', 'chunksize')),
                                        passes=int(config.get('topic', 'passes')),
                                        minimum_probability=float(config.get('topic', 'minimum_probability'))
                                        )
    #ldamodel = models.ldamulticore.LdaMulticore(corpus,
    #                                        num_topics=config.NUMBER_OF_TOPICS,
    #                                        id2word = dictionary,
    #                                        passes=1)
    #ldamodel.minimum_probability = 0.0
    dt = ldamodel.get_document_topics(corpus,minimum_probability=0.0)

    probable_words = []
    for i in range(0, int(config.get('topic', 'num_topics'))):
        terms = [dictionary[word_id] for word_id, score in ldamodel.get_topic_terms(i, topn=int(config.get('topic', 'num_top_words')))]
        probable_words.append({'topicId': 'topic_'+str(i),
                               'keywords': terms})
    final_dt = []
    for doc in dt:
        final_dt.append([a[1] for a in doc])
    #print probable_words
    logger.info('LDA Model Trained!')
    return final_dt, dt, X, vocab, probable_words



def calculate_information_gain(feature, topic):
    feature_stats = feature[1]
    entropy_old = find_initial_entropy(feature_stats, topic)
    avg_entropy_new = calculate_avg_entropy(feature_stats, topic)
    ig = entropy_old - avg_entropy_new
    return ig



def find_initial_entropy(feature_stats, topic):
    topic_text = 'topic_'+str(topic)+'_'
    if topic_text+'0' in feature_stats['topics_counts']:
        topic_zeros = feature_stats['topics_counts'][topic_text+'0']
    else:
        topic_zeros = 0
    if topic_text+'1' in feature_stats['topics_counts']:
        topic_ones = feature_stats['topics_counts'][topic_text+'1']
    else:
        topic_ones = 0
    tc = topic_zeros + topic_ones
    all_c = feature_stats['zeros_counts'] + feature_stats['ones_counts']

    if tc == 0:
        init_entropy = 0.0
    else:
        init_entropy = -(float(tc)/all_c)*math.log(float(tc)/all_c)
    return init_entropy


def calculate_avg_entropy(feature_stats, topic):
    topic_text = 'topic_'+str(topic)+'_'
    if topic_text+'0' in feature_stats['topics_counts']:
        topic_zeros = feature_stats['topics_counts'][topic_text+'0']
    else:
        topic_zeros = 0
    if topic_text+'1' in feature_stats['topics_counts']:
        topic_ones = feature_stats['topics_counts'][topic_text+'1']
    else:
        topic_ones = 0

    zeros = feature_stats['zeros_counts']
    ones = feature_stats['ones_counts']

    p0 = float(topic_zeros)/zeros
    p1 = float(topic_ones)/ones

    avg_weight_0 = float(zeros) / (zeros + ones)
    avg_weight_1 = float(ones) / (zeros + ones)

    if p1== 0 and p0 == 0:
        return 0.0
    elif p0 == 0:
        return -avg_weight_1*p1*math.log(p1)
    elif p1== 0:
        return -avg_weight_0*p0*math.log(p0)
    else:
        return -avg_weight_1*p1*math.log(p1) - avg_weight_0*p0*math.log(p0)


def find_words_per_topic(vocab, doc_topics, occur_matrix, config):
    from operator import itemgetter
    doc_best_topics = [max(doc,key=itemgetter(1))[0] for doc in doc_topics]
    features_stats = calculate_features_stats(doc_best_topics, occur_matrix, config)
    topics_representation = {}
    for topic in range(len(list(doc_topics)[0])):
        features_igs = []
        for feature in features_stats.items():
            feature_ig = calculate_information_gain(feature, topic)
            features_igs.append((feature[0],feature_ig))
        best_features_for_topic = sorted(features_igs,
                                         key=lambda tup: tup[1],
                                         reverse=True)[:int(config.get('topic', 'num_top_words'))]
        topics_representation['topic_'+str(topic)] = best_features_for_topic

    topics_best_words = []
    for topic, values in topics_representation.iteritems():
        #topics_words = {topic}
        #topics_words[topic] = []
        topics_words = {'topicId': topic,
                        'keywords': []}
        for feature in values:
            topics_words['keywords'].append(find_word(feature[0], vocab))
        topics_best_words.append(topics_words)

    return topics_best_words


def find_word(feature, vocab):
    index_feature = feature.split('_')[1]
    return vocab[int(index_feature)]


def calculate_features_stats(doc_best_topics, occur_matrix, config):
    """Construct a dict of the form:
        {feature1:{zero_counts:N, ones_counts:M,
                   t1_0_counts:X, t1_1_counts:Y,..}}
    """
    features_stats = {}
    word_occur_min = len(occur_matrix.nonzero()[0]) / occur_matrix.shape[1]

    for index, feature in enumerate(occur_matrix.T):
        ones = len(feature.nonzero()[0])
        if ones > 100:
            zeros = feature.shape[1] - ones
            topic_counts = calculate_topic_counts(feature, doc_best_topics, config)
            features_stats['feature_'+str(index)] = {'zeros_counts':zeros,
                                                'ones_counts':ones,
                                                'topics_counts':topic_counts,
                                                }
    return features_stats


def calculate_topic_counts(feature, doc_best_topics, config):
    topics_ids = [x for x in range(int(config.get('topic', 'num_topics')))]
    topics = {}
    nonzeros = feature.nonzero()
    topics_nonzeros = [doc_best_topics[i] for i in nonzeros[1]]
    topics_counts = [doc_best_topics.count(tid) for tid in topics_ids]
    for tid in topics_ids:
        topics['topic_'+str(tid)+'_1'] = topics_nonzeros.count(tid)
        topics['topic_'+str(tid)+'_0'] = (doc_best_topics.count(tid) -
                                          topics_nonzeros.count(tid))

    return topics

def update_graph_topics(graph, docs, config):
    """Updates the graph with the topics and topic distributions of users.

    Args:
        -graph: networkx format of graph
        - docs: List with concatenated strings for each user
        - list_docs: List of list of strings Each sublist contains
           all the the tweets/posts etc done by the user.
        -config: Config object from main file

    Returns:
        -clean_G: networkx object of updated graph
    """




    document_topic, document_topic_old, document_term, vocab, probable_words = nfm_extraction(docs, config)
    topic_representations = find_words_per_topic(vocab, document_topic_old, document_term, config)
    clean_G = networkx.Graph()
    out_G = networkx.Graph()
    influence_dict = graph_influence(graph)
    logger.info('Calculated Influence!')
    for i, node in enumerate(graph.nodes()):
        #print node
        tmp_td = document_topic[i]
        tmp_tid = str(tmp_td.index(max(tmp_td)))
        for topic_repr in topic_representations:
            if topic_repr['topicId'] == 'topic_'+tmp_tid:
                tmp_t = topic_repr['keywords']
        clean_G.add_node(node, text=docs[i], label=node, topic_distr=tmp_td,
                         topic_id = 'topic_'+tmp_tid)
        out_G.add_node(node, label=node)
        words_str = ''
        for cc,word in enumerate(tmp_t):
            if cc == 0:
                words_str = words_str + word
            else:
                words_str = words_str + ' ' + word
        clean_G.node[node]['topic_full'] = words_str
        clean_G.node[node]['topic_repr'] = ' '.join(tmp_t[0:3])
        clean_G.node[node]['mean_infl'] = influence_dict[node]
        out_G.node[node]['mean_infl'] = influence_dict[node]
        out_G.node[node]['topic_full'] = words_str
        out_G.node[node]['topic_repr'] = ' '.join(tmp_t[0:3])
        #break
    for edge in graph.edges():
        clean_G.add_edge(*edge)
        out_G.add_edge(*edge)
    return clean_G, out_G


