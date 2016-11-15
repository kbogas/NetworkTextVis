import networkx as networkx
import logging
import json
from bson.json_util import loads
from visualizations import chord_diagram_create
from text import update_graph_topics
#from ranking import graph_influence
import subprocess
import pprint

logger = logging.getLogger('universal_logger')

def read_network(config, scheme):

    """ Read network from file.

    Args:
        - config: Config object from main file
        - scheme: The form the input takes. Can be one of the following:
          ['edge', 'json', 'gexf', 'matrix']
    Returns:
        - G: The graph read, as a  networkx object

    """

    #scheme = config.get('network', 'scheme')
    possible_schemes = ['edge', 'json', 'gexf', 'adjlist', 'twitter']
    if scheme not in possible_schemes:
        logger.error('Selected scheme %s is not recognized!' % (scheme))
        print 'Use one of the following instead:'
        for sc in possible_schemes:
            print '-- %s --' % sc
        exit(1)
    configs = dict(config.items(scheme))
    #print configs
    if scheme == 'edge':
        edgelist_path = config.get(scheme, 'path_to_edgelist')
        node_path = config.get(scheme, 'path_to_nodelist')
        with open(edgelist_path, 'r') as edgelist_fname:
            with open(node_path, 'r') as node_fname:
                G = edgelist_load(edgelist_fname, node_fname)
    elif scheme == 'json':
        inpath = config.get(scheme, 'path_to_json')
        with open(inpath, 'r') as infile:
            G = json_load(infile)
    elif scheme == 'gexf':
        inpath = config.get(scheme, 'path_to_gexf')
        G = networkx.read_gexf(inpath)
    elif scheme == 'adjlist':
        adjlist_path = config.get(scheme, 'path_to_adjlist')
        node_path = config.get(scheme, 'path_to_nodelist')
        with open(adjlist_path, 'r') as adjlist_fname:
            with open(node_path, 'r') as node_fname:
                G = adjlist_load(adjlist_fname, node_fname)
    elif scheme == 'twitter':
        twitter_path = config.get(scheme, 'path_to_twitter')
        with open(twitter_path, 'r') as twitter_fname:
            G = create_twitter_net(twitter_fname)
    if networkx.is_directed(G):
        type1 = 'directed'
    else:
        type1 = 'undirected'
    logger.info('Loaded %s graph with: %i nodes and %i edges' % (type1, len(G.nodes()), len(G.edges())))
    return G


def gather_texts(graph, config, scheme):

    """ Gathers the posts/tweets etc of a person.

    Args:
        - graph: The graph object, in networkx format
        - config: Config object from main file
    Returns:
        - documents: List with concatenated strings for each user
        - list_docs: List of list of strings Each sublist contains
           all the the tweets/posts etc done by the user.

    """

    objects = []
    documents = []
    list_docs = []
    # If texts already gather in the input network. If yes will use text_field
    # in order to read the gathered posts
    gathered = config.getboolean('data', 'gathered')
    # Appropriate attribute name with dictionary of the posts/tweets etc.
    attribute = config.get('data', 'attribute')
    # Appropriate attribute name for the posts field
    text_field = config.get('data', 'text_field')
    label = config.get('main', 'label')
    count_failed = 0
    if not(gathered):
        for i in list(graph.nodes()):
            try:
                #print graph.node[i].keys()
                #print graph.node[i][attribute]
                #print loads(graph.node[i][attribute],strict=False)
                objects.append(loads(graph.node[i][attribute],strict=False))
            except Exception, e:
                pprint.pprint(e)
                logger.warning('Node %s could not gather texts, due to parsing errors' % (str(graph.node[i][label])))
                count_failed += 1
                graph.remove_node(i)
        print len(objects)
        for o in objects:
            if scheme == 'twitter':
                posts = o
            else:
                posts = o[attribute]
            concat_post = ''
            tmp_doc = []
            for p in posts:
                concat_post = concat_post + ' ' + p[text_field]
                tmp_doc.append(p[text_field])
            documents.append(concat_post)
            list_docs.append(tmp_doc)
    else:
        for i in list(graph.nodes()):
            try:
                #print "Posts"
                #print graph.node[i][attribute]
                #break
                #print "Inside of Posts"
                #print loads(graph.node[i][attribute],strict=False)
                #print "Inside of Posts2"
                if text_field != attribute:
                    posts = loads(graph.node[i][attribute],strict=False)[attribute]
                    concat_post = ''
                    tmp_doc = []
                    for p in posts:
                        concat_post = concat_post + ' ' + p[text_field]
                        tmp_doc.append(p[text_field])
                    documents.append(concat_post)
                    list_docs.append(tmp_doc)
                else:
                    documents.append(graph.node[i][attribute])
                    list_docs.append(graph.node[i][attribute])
            except Exception:
                logger.warning('Node %s could not gather texts, due to parsing errors' % (str(graph.node[i][label])))
                count_failed += 1
                graph.remove_node(i)
            #break
            #list_docs = documents
    logger.info("Number of nodes with gathered texts: %i" % len(documents))
    if count_failed > 0 :
        logger.warning("Could not load: %i users!" % count_failed)
    print len(documents)
    #print documents
    return documents, list_docs


def json_load(fname):
    '''
        Load from .json file.
        Args:
            - fname : file object from open()

        Returns:
            - G: Loaded directed/undirected graph

    '''
    d = json.load(fname)
    try:
        if d['directed']==True:
            G = networkx.DiGraph()
        else:
            G = networkx.Graph()
    except KeyError:
        G = networkx.Graph()
    G.add_nodes_from(d['nodes'])
    G.add_edges_from(d['edges'])
    
    return G


def adjlist_load(adjlist_fname, node_fname):
    '''
        Load from .adjlist file the structure of the network
        and the node attributes from node_fname

        Args:
            - adjlist_fname : file object from .adjlist file
            - node_fname : file object from .json node file
        Returns:
            - G: Loaded graph

    '''

    G = networkx.read_adjlist(adjlist_fname)
    nodes = json.load(node_fname)
    G.add_nodes_from(nodes['nodes'])
    return G

def edgelist_load(edgelist_fname, node_fname):
    '''
        Load from .edgelist file the structure of the network
        and the node attributes from node_fname

        Args:
            - edgelist_fname : file object from .edgelist file
            - node_fname : file object from .json node file
        Returns:
            - G: Loaded graph

    '''
    G = networkx.read_edgelist(edgelist_fname)
    nodes = json.load(node_fname)
    G.add_nodes_from(nodes['nodes'])
    return G

def create_twitter_net(fname):
    '''
        Create network from twitter crawl, directly from api.
        Construct the network as mentions between users' tweets.

        Args:
            - twitter_fname : file object from .json twitter crawl file
        Returns:
            - G: Constructed graph

    '''

    G = networkx.Graph()
    error_count = 0
    data = []
    for line in fname:                        
        try: 
            tweet = json.loads(line)
            data.append(tweet)
        except:
            logger.info('Error in tweets.json!')
            error_count += 1
    for i in xrange(len(data)):
        cur_id = data[i]['user']['screen_name']
        if cur_id in G.nodes():
            G.node[cur_id]['posts'].append({ 'tweet_id':data[i]['id'], 'text':data[i]['text']})
        else:
            G.add_node(cur_id,label=data[i]['user']['screen_name'], posts=[{ 'tweet_id':data[i]['id'], 'text':data[i]['text']}])
        mentions = data[i]['entities']['user_mentions']
        if mentions:
            for mention in mentions:
                if mention['screen_name'] in G.nodes():
                    G.add_edge(cur_id, mention['screen_name'])
    for node in G.nodes():
        G.node[node]['posts'] = json.dumps(G.node[node]['posts'])
    logger.info("Parsed: %i tweets, with %i errors!" % (len(data), error_count))
    return G

def network_create(G, docs, config):
    """
        Create the final .gexf file needed form visualizing the network
        Args:
            - G : generated graph
            - docs: list of strings, one for each node(concatenated)
            - config: config file

    """
    logger.info('Starting Topic Module!')
    G, out_G = update_graph_topics(G, docs, config)
    logger.info('Finished Topic Modeling!')
    out_path = config.get('out_gexf', 'path_to_gexf')
    jar_path = config.get('out_gexf', 'path_to_jar')
    final_out_path = config.get('out_gexf', 'path_to_final_gexf')
    logger.info('Will write temporary gexf to: %s' % out_path)
    networkx.write_gexf(out_G, out_path)
    logger.info('Will run jar layout mechanism from: %s \n Reads from: %s \n Writes to: %s' % (jar_path, out_path, final_out_path))
    subprocess.call(['java', '-jar', jar_path, out_path, final_out_path])
    logger.info('Created Final Gexf!')
    return 0


def execute_task(G, docs, list_docs, config, scheme, task):

    """
        Execute each visualization task.
        Args:
            - G : generated graph
            - docs: list of strings, one for each node(concatenated)
            - list_docs: list of list of strings, one list of posts for
                each node
            - config: config file
            - scheme: input file type
            - task: tasl at hand
        Returns:
            Nothing. Just executes the appropriate task
    """

    if task == 'network':
        network_create(G, docs, config)
    elif task == 'chord':
        chord_diagram_create(list_docs, config)
    return 0
